from time import sleep
from typing import Optional
import pytest
from app.shared.networking import Packet
from app.messaging.messages import MessageMapper
from app.messaging.topology import ImAliveMessage, NetTopologyMessage
from app.messaging.message_broker import MessageBroker
from app.shared.networking import ConnectionSettings


class ConnectionSettingsFactory:
    @staticmethod
    def sample():
        return ConnectionSettings('1.2.3.4', 6789)


class NetworkConnectionMock:
    def __init__(self):
        self.sent_by_broker = []
        self.to_receive = []

    def send(self, packet: Packet):
        self.sent_by_broker.append(packet)

    def receive(self) -> Optional[Packet]:
        if self.to_receive:
            element = self.to_receive[-1]
            del self.to_receive[-1]
            return element
        return None


def wait_for_response():
    sleep(0.1)


@pytest.fixture()
def connection():
    result = NetworkConnectionMock()
    broker = MessageBroker(result)
    broker.start()
    yield result
    broker.stop()
    broker.join()


@pytest.fixture()
def mapper():
    result = MessageMapper() \
        .register(ImAliveMessage) \
        .register(NetTopologyMessage)
    yield result


def test_imalive_receiveImalive_sendNettopo(
        connection: NetworkConnectionMock,
        mapper: MessageMapper
        ):
    given_address = ConnectionSettingsFactory.sample()
    given_packet = Packet(b'IMALIVE{}', given_address)
    connection.to_receive = [given_packet]

    wait_for_response()

    sent_packet: Packet = connection.sent_by_broker[0]
    message = mapper.map_from_bytes(sent_packet.data)
    assert sent_packet.address == given_address
    assert isinstance(message, NetTopologyMessage)
