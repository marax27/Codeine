from __future__ import annotations
from abc import ABC, abstractmethod
from re import search
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass, InitVar, field
from dataclasses_json import dataclass_json
from app.shared.networking import ConnectionSettings


@dataclass(frozen=False)
class CommandContext:
    sender_address: ConnectionSettings = None
    local_address: ConnectionSettings = None

    def initialize(self,
                   sender_address: ConnectionSettings,
                   local_address: ConnectionSettings):
        self.sender_address = sender_address
        self.local_address = local_address


@dataclass_json
@dataclass(frozen=True)
class Command(ABC):

    context: InitVar[CommandContext] = field(default=CommandContext(),
                                             init=False)

    @classmethod
    @abstractmethod
    def get_identifier(cls) -> str:
        pass

    @abstractmethod
    def invoke(self, receiver: Any) -> List[Command]:
        pass


class CommandMapper:
    def __init__(self):
        self._registered_commands: Dict[str, type] = dict()

    def register(self, command_type: type) -> CommandMapper:
        identifier = command_type.get_identifier()
        self._registered_commands[identifier] = command_type
        return self

    def map_to_bytes(self, command: Command) -> bytes:
        self._assert_registered(command.get_identifier())
        code = command.to_json()
        return (command.get_identifier() + code).encode('utf-8')

    def map_from_bytes(self, data: bytes) -> Command:
        identifier, code = self._parse(data.decode('utf-8'))
        self._assert_registered(identifier)

        command_type = self._registered_commands[identifier]
        return command_type.from_json(code)

    def _parse(self, text: str) -> Tuple[str, str]:
        index = search(r'[^A-Z]', text).start()
        return text[:index], text[index:]

    def _assert_registered(self, identifier: str):
        if identifier not in self._registered_commands:
            raise CommandTypeNotRegisteredError(identifier)


class CommandTypeNotRegisteredError(Exception):
    pass
