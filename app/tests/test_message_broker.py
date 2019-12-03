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

    @staticmethod
    def other():
        return ConnectionSettings('1.2.3.5', 6789)


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


def get_imalive_packet(address: ConnectionSettings) -> Packet:
    return Packet(b'IMALIVE{}', address)


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
    given_packet = get_imalive_packet(given_address)
    connection.to_receive = [given_packet]

    wait_for_response()

    sent_packet: Packet = connection.sent_by_broker[0]
    message = mapper.map_from_bytes(sent_packet.data)
    assert sent_packet.address == given_address
    assert isinstance(message, NetTopologyMessage)


def test_nettopo_receiveImalive_nettopoDoesntContainOurAddress(
        connection: NetworkConnectionMock,
        mapper: MessageMapper
        ):
    given_address = ConnectionSettingsFactory.sample()
    given_packet = get_imalive_packet(given_address)

    connection.to_receive = [given_packet]
    wait_for_response()

    sent_packet: Packet = connection.sent_by_broker[0]
    message: NetTopologyMessage = mapper.map_from_bytes(sent_packet.data)
    assert given_address not in message.agents


def test_nettopo_nettopoWithAgentsThenImalive_brokerSendsPreviouslyAcquiredAgents(
        connection: NetworkConnectionMock,
        mapper: MessageMapper
        ):
    given_addresses = [ConnectionSettingsFactory.other()]
    sender_address = ConnectionSettingsFactory.sample()
    given_message = NetTopologyMessage(given_addresses)
    message_as_bytes = mapper.map_to_bytes(given_message)
    given_packet = Packet(message_as_bytes, sender_address)

    connection.to_receive.append(given_packet)
    wait_for_response()

    connection.to_receive.append(get_imalive_packet(sender_address))
    wait_for_response()

    sent_packet: Packet = connection.sent_by_broker[0]
    message: NetTopologyMessage = mapper.map_from_bytes(sent_packet.data)
    assert set(given_addresses) == set(message.agents)
