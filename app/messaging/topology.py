from dataclasses import dataclass
from typing import Tuple
from dataclasses_json import dataclass_json
from app.shared.networking import ConnectionSettings
from .messages import Message


@dataclass_json
@dataclass(frozen=True)
class ImAliveMessage(Message):
    @classmethod
    def get_identifier(cls) -> str:
        return "IMALIVE"


@dataclass_json
@dataclass(frozen=True)
class NetTopologyMessage(Message):
    agents: Tuple[ConnectionSettings, ...]

    @classmethod
    def get_identifier(cls) -> str:
        return "NETTOPO"
