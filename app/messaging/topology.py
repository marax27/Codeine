from dataclasses import dataclass
from typing import Tuple
from app.shared.networking import ConnectionSettings
from .messages import Message


@dataclass(frozen=True)
class AgentState:
    last_notification_time: float


@dataclass(frozen=True)
class ImAliveMessage(Message):
    @classmethod
    def get_identifier(cls) -> str:
        return "IMALIVE"


@dataclass(frozen=True)
class NetTopologyMessage(Message):
    agents: Tuple[ConnectionSettings, ...]

    @classmethod
    def get_identifier(cls) -> str:
        return "NETTOPO"
