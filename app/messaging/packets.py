from abc import ABC, abstractmethod
from app.shared import json


class Message(ABC):
    @abstractmethod
    def get_identifier(self) -> str:
        pass

    def to_bytes(self) -> bytes:
        obj = self.__dict__
        code = json.from_object(obj)
        return (self.get_identifier() + code).encode('utf-8')
