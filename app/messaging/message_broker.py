from queue import Queue
from typing import Dict, Iterable
from app.shared.multithreading import StoppableThread
from app.shared.networking import Packet, ConnectionSettings, NetworkConnection
from .messages import MessageMapper, Message
from .topology import ImAliveMessage, NetTopologyMessage


class MessageBroker(StoppableThread):
    def __init__(self, connection_settings: ConnectionSettings):
        super().__init__()
        self._connection = NetworkConnection(connection_settings)
        self._message_queue = Queue()
        self._packet_queue = Queue()
        self._message_mapper = self._create_message_mapper()
        self._agents: Dict[ConnectionSettings, float] = dict()

    def get_messages(self) -> Iterable[Message]:
        while not self._message_queue.empty():
            yield self._message_queue.get()

    def run(self):
        while not self.requested_stop():
            self._handle_incoming_message()
            self._handle_outgoing_messages()

    def _handle_incoming_message(self):
        received = self._connection.receive()
        if received is not None:
            self._message_queue.put(received)

    def _handle_outgoing_messages(self):
        while not self._message_queue.empty():
            _ = self._message_queue.get()

    def _create_message_mapper(self) -> MessageMapper:
        return MessageMapper() \
            .register(ImAliveMessage) \
            .register(NetTopologyMessage)
