import pytest

from app.messaging.topology import NetTopologyMessage, ImAliveMessage
from app.messaging.messages import MessageMapper
from app.shared.networking import ConnectionSettings


class NetTopologyMessageFactory:
    @staticmethod
    def create() -> NetTopologyMessage:
        network_connection_1 = ConnectionSettings('192.168.192.1', 2137)
        network_connection_2 = ConnectionSettings('192.168.192.2', 2137)
        agents = (network_connection_1, network_connection_2)
        message = NetTopologyMessage(agents)
        return message


class MapperFactory:
    @staticmethod
    def create(type_to_register: type) -> MessageMapper:
        return MessageMapper().register(type_to_register)


def test_nettopologyMapping_sampleMessage_messageMappedCorrectly():
    message = NetTopologyMessageFactory().create()

    mapper = MapperFactory().create(NetTopologyMessage)
    message_as_bytes = mapper.map_to_bytes(message)
    message_from_bytes = mapper.map_from_bytes(message_as_bytes)

    assert message_from_bytes == message


def test_imaliveMapping_sampleMessage_messageMappedCorrectly():
    message = ImAliveMessage()
    mapper = MapperFactory().create(ImAliveMessage)

    message_as_bytes = mapper.map_to_bytes(message)
    message_from_bytes = mapper.map_from_bytes(message_as_bytes)

    assert message_from_bytes == message


def test_imaliveMapping_sampleMessage_byteMessageContainsMessageId():
    message = ImAliveMessage()
    message_id = message.get_identifier()
    mapper = MessageMapper().register(ImAliveMessage)

    message_as_bytes = mapper.map_to_bytes(message)

    assert message_id.encode('UTF-8') in message_as_bytes


def test_imaliveMapping_sampleMessage_byteMessageContainsEmptyBrackets():
    message = ImAliveMessage()
    mapper = MapperFactory().create(ImAliveMessage)

    message_as_bytes = mapper.map_to_bytes(message)

    assert b'{}' in message_as_bytes
