from queue import Queue
from typing import Dict, Iterable, Optional
from app.shared.multithreading import StoppableThread
from app.shared.networking import Packet, ConnectionSettings, NetworkConnection
from .messages import MessageMapper, Message
from .topology import ImAliveMessage, NetTopologyMessage


class MessageBroker(StoppableThread):
    def __init__(self, connection_settings: ConnectionSettings):
        super().__init__()
        self._connection = NetworkConnection(connection_settings)
        self._send_queue = Queue()
        self._recv_queue = Queue()
        self._message_mapper = self._create_message_mapper()
        self._agents: Dict[ConnectionSettings, float] = dict()

    def get_messages(self) -> Iterable[Message]:
        while not self._recv_queue.empty():
            yield self._recv_queue.get()

    def run(self):
        while not self.requested_stop():
            self._handle_incoming_message()
            self._handle_outgoing_messages()

    def _handle_incoming_message(self):
        packet = self._connection.receive()
        if packet is not None:
            try:
                message = self._to_message(packet.data)
                self._recv_queue.put(message)
            except Exception:
                return

    def _handle_outgoing_messages(self):
        while not self._send_queue.empty():
            _ = self._send_queue.get()

    def _to_message(self, data: bytes) -> Message:
        return self._message_mapper.map_from_bytes(data)

    def _create_message_mapper(self) -> MessageMapper:
        return MessageMapper() \
            .register(ImAliveMessage) \
            .register(NetTopologyMessage)
