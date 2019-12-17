from time import sleep
from queue import Queue, Empty
from typing import Optional
import pytest
from app.shared.networking import Packet, NetworkIO
from app.messaging.commands import CommandMapper
from app.messaging.topology import ImAliveCommand, NetTopologyCommand
from app.messaging.broker import Broker
from app.shared.networking import ConnectionSettings


class ConnectionSettingsFactory:
    @staticmethod
    def sample():
        return ConnectionSettings('1.2.3.4', 6789)

    @staticmethod
    def other():
        return ConnectionSettings('1.2.3.5', 6789)


class NetworkIOMock(NetworkIO):
    def __init__(self):
        self.outgoing = Queue()
        self.incoming = Queue()

    def send(self, packet: Packet):
        self.outgoing.put(packet)

    def receive(self) -> Optional[Packet]:
        if not self.incoming.empty():
            try:
                return self.incoming.get_nowait()
            except Empty:
                pass
        return None

    def get_address(self) -> ConnectionSettings:
        return ConnectionSettings('412.412.412.412', 99999)


def wait_for_response():
    sleep(0.1)


def get_imalive_packet(address: ConnectionSettings) -> Packet:
    return Packet(b'IMALIVE{}', address)


@pytest.fixture()
def connection():
    result = NetworkIOMock()
    broker = Broker(result)
    broker.start()
    yield result
    broker.stop()
    broker.join()


@pytest.fixture()
def mapper():
    result = CommandMapper() \
        .register(ImAliveCommand) \
        .register(NetTopologyCommand)
    yield result


def test_imalive_receiveImalive_sendNettopo(
        connection: NetworkIOMock,
        mapper: CommandMapper
        ):
    given_address = ConnectionSettingsFactory.sample()
    given_packet = get_imalive_packet(given_address)
    connection.incoming.put(given_packet)

    wait_for_response()

    sent_packet: Packet = connection.outgoing.get_nowait()
    command = mapper.map_from_bytes(sent_packet.data)
    assert sent_packet.address == given_address
    assert isinstance(command, NetTopologyCommand)


def test_nettopo_sendBrokerItsAddress_brokerDoesntRegisterTheAddress(
        connection: NetworkIOMock,
        mapper: CommandMapper
        ):
    given_address = connection.get_address()
    sender_address = ConnectionSettingsFactory.sample()
    given_command = NetTopologyCommand([given_address])
    command_as_bytes = mapper.map_to_bytes(given_command)
    given_packet = Packet(command_as_bytes, sender_address)

    connection.incoming.put(given_packet)
    wait_for_response()

    connection.incoming.put(get_imalive_packet(sender_address))
    wait_for_response()

    sent_packet: Packet = connection.outgoing.get_nowait()
    command: NetTopologyCommand = mapper.map_from_bytes(sent_packet.data)
    assert given_address not in set(command.agents)
