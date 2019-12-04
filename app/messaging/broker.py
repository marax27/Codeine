from time import sleep
from queue import Queue
from typing import Iterable, Optional
from dataclasses import dataclass
from app.shared.multithreading import StoppableThread
from app.shared.networking import Packet, ConnectionSettings, NetworkConnection
from .commands import CommandMapper, Command
from .topology import Topology, ImAliveCommand, NetTopologyCommand


@dataclass(frozen=True)
class Payload:
    '''Command + information where to send it.'''
    command: Command
    recipient_id: Optional[int]


class Broker(StoppableThread):
    def __init__(self, connection: NetworkConnection):
        super().__init__()
        self._connection = connection
        self._send_queue = Queue()
        self._recv_queue = Queue()
        self._command_mapper = self._create_command_mapper()
        self._topology = Topology()

    def get_commands(self) -> Iterable[Command]:
        while not self._recv_queue.empty():
            yield self._recv_queue.get()

    def broadcast(self, command: Command):
        self.send_to(command, None)

    def send_to(self, command: Command, recipient_id: int):
        self._send_queue.put(Payload(command, recipient_id))

    def run(self):
        while not self.requested_stop():
            self._handle_incoming_packet()
            self._handle_outgoing_commands()
            sleep(0.01)

    def _handle_incoming_packet(self):
        packet = self._connection.receive()
        if packet is not None:
            try:
                command = self._to_command(packet.data)
            except Exception:
                return

            sender_address = packet.address
            self._topology.add_or_update(sender_address)

            identifier = command.get_identifier()
            if identifier == 'IMALIVE':
                self._handle_imalive(sender_address)
            elif identifier == 'NETTOPO':
                self._handle_nettopo(command)

    def _handle_outgoing_commands(self):
        while not self._send_queue.empty():
            payload: Payload = self._send_queue.get()
            command, recipient_id = payload.command, payload.recipient_id

            recipients = self._get_recipients_by_id(recipient_id)
            self._send(recipients, command)

    def _handle_imalive(self, sender_address: ConnectionSettings):
        all_addresses = self._topology.get_addresses()
        agents = tuple(a for a in all_addresses if a != sender_address)
        command = NetTopologyCommand(agents)
        self.send_to(command, hash(sender_address))

    def _handle_nettopo(self, command: NetTopologyCommand):
        self._topology.add_or_update_many(command.agents)

    def _to_command(self, data: bytes) -> Command:
        return self._command_mapper.map_from_bytes(data)

    def _get_recipients_by_id(self, recipient_id: Optional[int]) -> Iterable[ConnectionSettings]:
        if recipient_id is None:
            return self._topology.get_addresses()
        return {self._topology.get_address_by_id(recipient_id)}

    def _send(self, recipients: Iterable[ConnectionSettings], command: Command):
        command_as_bytes = self._command_mapper.map_to_bytes(command)
        for recipient in recipients:
            packet = Packet(command_as_bytes, recipient)
            self._connection.send(packet)

    def _create_command_mapper(self) -> CommandMapper:
        return CommandMapper() \
            .register(ImAliveCommand) \
            .register(NetTopologyCommand)
