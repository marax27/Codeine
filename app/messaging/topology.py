from dataclasses_json import dataclass_json
from dataclasses import dataclass
from typing import Tuple
from .messages import Message
from app.shared.networking import ConnectionSettings


@dataclass_json
@dataclass(frozen=True)
class ImAlive(Message):
    def get_identifier(self) -> str:
        return "IMALIVE"


@dataclass_json
@dataclass(frozen=True)
class NetTopology(Message):
    agents: Tuple[ConnectionSettings, ...]

    def get_identifier(self) -> str:
        return "NETTOPO"
