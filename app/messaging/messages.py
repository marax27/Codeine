from abc import ABC, abstractmethod
from re import search
from typing import Dict, Tuple
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True)
class Message(ABC):
    @abstractmethod
    def get_identifier(self) -> str:
        pass


class MessageMapper:
    def __init__(self):
        self._registered_messages: Dict[str, type] = dict()

    def register(self, message_type: type, identifier: str):
        self._registered_messages[identifier] = message_type
        return self

    def map_to_bytes(self, message: Message) -> bytes:
        self._assert_registered(message.get_identifier())
        code = message.to_json()
        return (message.get_identifier() + code).encode('utf-8')

    def map_from_bytes(self, data: bytes) -> Message:
        identifier, code = self._parse(data.decode('utf-8'))
        self._assert_registered(identifier)

        message_type = self._registered_messages[identifier]
        return message_type.from_json(code)

    def _parse(self, text: str) -> Tuple[str, str]:
        index = search(r'[^A-Z]', text).start()
        return text[:index], text[index:]

    def _assert_registered(self, identifier: str):
        if identifier not in self._registered_messages:
            raise MessageTypeNotRegisteredError(identifier)


class MessageTypeNotRegisteredError(Exception):
    pass
