from enum import Enum
from queue import Queue
from threading import Event, Thread
from app.shared.networking import Packet, ConnectionSettings, NetworkConnection


class MessageBroker(Thread):
    def __init__(self, connection_settings: ConnectionSettings):
        super().__init__()
        self._connection = NetworkConnection(connection_settings)
        self._send_queue = Queue()
        self._recv_queue = Queue()
        self._stop_event = Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            self._handle_incoming_message()
            self._handle_outgoing_messages()

    def _handle_incoming_message(self):
        received = self._connection.receive()
        if received is not None:
            self._recv_queue.put(received)

    def _handle_outgoing_messages(self):
        while not self._send_queue.empty():
            _ = self._send_queue.get()
