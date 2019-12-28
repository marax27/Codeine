from time import sleep
from queue import Queue, Empty
from typing import List, Optional
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


class BrokerContext:
    def __init__(self):
        self._mapper = CommandMapper()
        self._connection = NetworkIOMock()
        self._broker = Broker(self._connection, self._mapper)
        self._broker.start()

    def __del__(self):
        self.stop()

    def get_broker_address(self) -> ConnectionSettings:
        return self._connection.get_address()

    def wait_some(self, sleep_time: float = 0.1):
        '''Block execution for some time so that the broker thread
        can process whatever it received.'''
        sleep(sleep_time)

    def dump_outgoing_packets(self) -> List[Packet]:
        '''Return all packets send by the broker so far. These packets
        will not appear in another dump call.'''
        result = []
        while not self._connection.outgoing.empty():
            result.append(self._connection.outgoing.get_nowait())
        return result

    def send_to_broker(self, packet: Packet):
        self._connection.incoming.put(packet)

    def stop(self):
        if self._broker:
            self._broker.stop()
            self._broker.join()


@pytest.fixture()
def context():
    result = BrokerContext()
    yield result
    result.stop()


@pytest.fixture()
def mapper():
    return CommandMapper() \
        .register(ImAliveCommand) \
        .register(NetTopologyCommand)


def get_imalive_packet(address: ConnectionSettings) -> Packet:
    return Packet(b'IMALIVE{}', address)


def test_imalive_receiveImalive_sendNettopo(
        context: BrokerContext,
        mapper: CommandMapper
        ):
    given_address = ConnectionSettingsFactory.sample()
    given_packet = get_imalive_packet(given_address)

    context.send_to_broker(given_packet)

    context.wait_some()
    outgoing_packets = context.dump_outgoing_packets()

    assert len(outgoing_packets) == 1
    assert outgoing_packets[0].address == given_address

    outgoing_command = mapper.map_from_bytes(outgoing_packets[0].data)
    assert isinstance(outgoing_command, NetTopologyCommand)


def test_nettopo_sendBrokerItsAddress_brokerDoesntRegisterTheAddress(
        context: BrokerContext,
        mapper: CommandMapper
        ):
    given_address = context.get_broker_address()
    sender_address = ConnectionSettingsFactory.sample()
    given_command = NetTopologyCommand([given_address])
    command_as_bytes = mapper.map_to_bytes(given_command)
    given_packet = Packet(command_as_bytes, sender_address)

    context.send_to_broker(given_packet)
    context.wait_some()

    context.send_to_broker(get_imalive_packet(sender_address))
    context.wait_some()

    outgoing_packets = context.dump_outgoing_packets()
    assert len(outgoing_packets) == 1

    packet_data = outgoing_packets[0].data
    command: NetTopologyCommand = mapper.map_from_bytes(packet_data)
    assert given_address not in set(command.agents)
