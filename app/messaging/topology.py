from __future__ import annotations
from abc import abstractmethod
from time import time
from typing import ClassVar, Dict, Iterable, Tuple
from dataclasses import dataclass
from app.shared.networking import ConnectionSettings
from .commands import Command, Broadcast, ReturnToSender, CommandDestination


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

    def add_or_update(self, address: ConnectionSettings):
        self._agents[address] = AgentState.create()

    def add_or_update_many(self, addresses: Iterable[ConnectionSettings]):
        for address in addresses:
            self.add_or_update(address)

    def get_addresses(self) -> Iterable[ConnectionSettings]:
        return self._agents.keys()

    def get_address_by_id(self, identifier: int) -> ConnectionSettings:
        matches = [a for a in self.get_addresses() if hash(a) == identifier]
        if len(matches) != 1:
            raise AgentIdentifierNotFoundError(identifier)
        return matches[0]


class AgentIdentifierNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class NetworkCommand(Command):
    @abstractmethod
    def invoke(self, receiver: Topology) -> Iterable[Command]:
        pass


@dataclass(frozen=True)
class ImAliveCommand(NetworkCommand):
    response_destination: ClassVar[CommandDestination] = ReturnToSender()

    @classmethod
    def get_identifier(cls) -> str:
        return "IMALIVE"

    def invoke(self, receiver: Topology) -> Iterable[Command]:
        yield NetTopologyCommand(agents=receiver.get_addresses())


@dataclass(frozen=True)
class NetTopologyCommand(NetworkCommand):
    agents: Tuple[ConnectionSettings, ...]

    @classmethod
    def get_identifier(cls) -> str:
        return "NETTOPO"

    def invoke(self, receiver: Topology) -> Iterable[Command]:
        receiver.add_or_update_many(self.agents)
        yield from ()
