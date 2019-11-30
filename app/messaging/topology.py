from dataclasses import dataclass
from typing import Tuple
from dataclasses_json import dataclass_json
from app.shared.networking import ConnectionSettings
from .messages import Message


@dataclass_json
@dataclass(frozen=True)
class ImAliveMessage(Message):
    def get_identifier(self) -> str:
        return "IMALIVE"


@dataclass_json
@dataclass(frozen=True)
class NetTopologyMessage(Message):
    agents: Tuple[ConnectionSettings, ...]

    def get_identifier(self) -> str:
        return "NETTOPO"
