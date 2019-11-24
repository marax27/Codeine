from typing import Tuple
from dataclasses import dataclass
import pytest

from app.messaging.packets import Message


@dataclass(frozen=True)
class SampleMessage(Message):
    identifier: int
    values: Tuple[Tuple[int, int], ...]

    def get_identifier(self) -> str:
        return 'SAMPLEMSG'


class MessageFactory:
    @staticmethod
    def sample() -> Message:
        return SampleMessage(42, ((1, 2),))


def test_messageCreation_sampleMessage_expectedIdentifier():
    given_message = MessageFactory.sample()
    assert given_message.get_identifier() == 'SAMPLEMSG'


def test_messageCreation_sampleMessage_expectedBytes():
    given_message = MessageFactory.sample()
    data = given_message.to_bytes()
    assert data == b'SAMPLEMSG{"identifier": 42, "values": [[1, 2]]}'
