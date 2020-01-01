from time import sleep
from queue import Queue
from typing import Iterable, Optional
from app.shared.multithreading import StoppableThread
from app.shared.networking import Packet, ConnectionSettings, NetworkIO
from app.computing.domain_commands import BaseDropCommand
from .commands import CommandMapper, Command
from .topology import Topology, NetworkCommand, ImAliveCommand, NetTopologyCommand
from .command_handler import CommandHandler, CommandNotRegisteredException, Payload
from .topology import ImAliveCommand, NetTopologyCommand


class Broker(StoppableThread):
    def __init__(self, connection: NetworkIO, mapper: CommandMapper):
        super().__init__()
        self._connection = connection
        self._command_mapper = mapper
        self._topology = Topology().with_forbidden(connection.get_address())
        self._send_queue = Queue()
        self._recv_queue = Queue()
        self._command_handler = self._create_command_handler()
        self._command_mapper.register(ImAliveCommand)
        self._command_mapper.register(NetTopologyCommand)

    def get_payloads(self) -> Iterable[Payload]:
        while not self._recv_queue.empty():
            yield self._recv_queue.get()

    def broadcast(self, command: Command):
        self.send(Payload(command, None))

    def discover_network(self):
        command = ImAliveCommand()
        port = self._connection.get_address().port
        LAN_broadcast_settings = ConnectionSettings('<broadcast>', port)
        self.send(Payload(command, LAN_broadcast_settings))

    def send(self, payload: Payload):
        self._send_queue.put(payload)

    def run(self):
        while not self.requested_stop():
            self._handle_incoming_packet()
            self._handle_outgoing_commands()
            sleep(0.01)

    def _handle_incoming_packet(self):
        packet = self._connection.receive()
        if packet is None:
            return

        try:
            payload = self._to_payload(packet)
        except Exception:
            return

        self._topology.add_or_update(packet.address)

        try:
            responses = self._command_handler.handle(payload)
            for response in responses:
                self.send(response)
        except CommandNotRegisteredException:
            self._recv_queue.put(payload)

    def _handle_outgoing_commands(self):
        while not self._send_queue.empty():
            payload: Payload = self._send_queue.get()
            recipients = self._topology.get_addresses(payload.address)
            self._send(recipients, payload.command)

    def _to_payload(self, packet: Packet) -> Payload:
        return Payload(self._to_command(packet.data), packet.address)

    def _to_command(self, data: bytes) -> Command:
        return self._command_mapper.map_from_bytes(data)

    def _send(self, recipients: Iterable[ConnectionSettings], command: Command):
        command_as_bytes = self._command_mapper.map_to_bytes(command)
        for recipient in recipients:
            packet = Packet(command_as_bytes, recipient)
            self._connection.send(packet)

    def _create_command_handler(self) -> CommandHandler:
        return CommandHandler() \
            .register(NetworkCommand, self._topology)
