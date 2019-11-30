from typing import Tuple
from dataclasses import dataclass
import pytest

from app.messaging.messages import Message, MessageMapper, MessageTypeNotRegisteredError


@dataclass(frozen=True)
class SampleMessage(Message):
    identifier: int
    values: Tuple[Tuple[int, int], ...]

    @classmethod
    def get_identifier(cls) -> str:
        return 'SAMPLEMSG'


class MessageFactory:
    @staticmethod
    def sample() -> Message:
        return SampleMessage(42, ((1, 2),))

    @staticmethod
    def other() -> Message:
        return SampleMessage(55, ((1, 2),))


class MapperFactory:
    @staticmethod
    def create() -> MessageMapper:
        return MessageMapper().register(SampleMessage)


def test_messageCreation_sampleMessage_expectedIdentifier():
    given_message = MessageFactory.sample()
    assert given_message.get_identifier() == 'SAMPLEMSG'


def test_mapToBytes_sampleMessage_expectedBytes():
    given_message = MessageFactory.sample()
    given_mapper = MapperFactory.create()

    data = given_mapper.map_to_bytes(given_message)
    assert data == b'SAMPLEMSG{"identifier": 42, "values": [[1, 2]]}'


def test_mapToBytes_unregisteredMessage_raise():
    given_message = MessageFactory.sample()
    given_mapper = MessageMapper()

    with pytest.raises(MessageTypeNotRegisteredError):
        given_mapper.map_to_bytes(given_message)


def test_mapFromBytes_jsonArray_convertToTuple():
    given_bytes = b'SAMPLEMSG{"identifier": 1, "values": [[5, 5], [6, 6]]}'
    given_mapper = MapperFactory.create()

    actual_message: SampleMessage = given_mapper.map_from_bytes(given_bytes)
    assert isinstance(actual_message.values, tuple)
    assert isinstance(actual_message.values[0], tuple)


def test_mapFromBytes_sampleBytes_expectedMessage():
    given_bytes = b'SAMPLEMSG{"identifier": 1, "values": [[5, 5], [6, 6]]}'
    given_mapper = MapperFactory.create()

    expected_message = SampleMessage(1, ((5, 5), (6, 6)))
    actual_message = given_mapper.map_from_bytes(given_bytes)
    assert expected_message == actual_message


def test_mapFromBytes_unregisteredMessage_raise():
    given_bytes = b'UNREGISTERED{"sample": 123}'
    given_mapper = MapperFactory.create()

    with pytest.raises(MessageTypeNotRegisteredError):
        given_mapper.map_from_bytes(given_bytes)
