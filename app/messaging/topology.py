from __future__ import annotations
from abc import abstractmethod
from time import time
from typing import Dict, Iterable, List, Optional, Set, Tuple
from dataclasses import dataclass
from app.shared.networking import ConnectionSettings
from .commands import Command


@dataclass(frozen=True)
class AgentState:
    last_connection_time: float

    @staticmethod
    def create() -> AgentState:
        return AgentState(time())


class Topology:
    """Stores information about registered agents present in the network."""

    def __init__(self):
        self._agents: Dict[ConnectionSettings, AgentState] = dict()
        self._forbidden: Set[ConnectionSettings] = set()

    def with_forbidden(self, address: ConnectionSettings) -> Topology:
        self._forbidden.add(address)
        return self

    def add_or_update(self, address: ConnectionSettings):
        if address not in self._forbidden:
            self._agents[address] = AgentState.create()

    def add_or_update_many(self, addresses: Iterable[ConnectionSettings]):
        for address in addresses:
            self.add_or_update(address)

    def get_all_addresses(self) -> Iterable[ConnectionSettings]:
        return self._agents.keys()

    def get_addresses(self, address: Optional[ConnectionSettings]) -> Iterable[ConnectionSettings]:
        all_addresses = self.get_all_addresses()
        if address is None:
            return all_addresses
        if address in all_addresses:
            return {address}
        raise RecipientNotRegisteredError()


@dataclass(frozen=True)
class NetworkCommand(Command):
    @abstractmethod
    def invoke(self, receiver: Topology) -> List[Command]:
        pass


@dataclass(frozen=True)
class ImAliveCommand(NetworkCommand):
    @classmethod
    def get_identifier(cls) -> str:
        return "IMALIVE"

    def invoke(self, receiver: Topology) -> List[Command]:
        return [NetTopologyCommand(agents=receiver.get_all_addresses())]


@dataclass(frozen=True)
class NetTopologyCommand(NetworkCommand):
    agents: Tuple[ConnectionSettings, ...]

    @classmethod
    def get_identifier(cls) -> str:
        return "NETTOPO"

    def invoke(self, receiver: Topology) -> List[Command]:
        receiver.add_or_update_many(self.agents)
        return []


class RecipientNotRegisteredError(Exception):
    pass
