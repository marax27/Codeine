from time import sleep, time
from queue import Queue
from typing import Dict, Iterable, Optional
from dataclasses import dataclass
from app.shared.multithreading import StoppableThread
from app.shared.networking import Packet, ConnectionSettings, NetworkConnection
from .messages import MessageMapper, Message
from .topology import AgentState, ImAliveMessage, NetTopologyMessage


@dataclass(frozen=True)
class Payload:
    '''Message + information where to send it.'''
    message: Message
    recipient_id: Optional[int]


class MessageBroker(StoppableThread):
    def __init__(self, connection_settings: ConnectionSettings):
        super().__init__()
        self._connection = NetworkConnection(connection_settings)
        self._send_queue = Queue()
        self._recv_queue = Queue()
        self._message_mapper = self._create_message_mapper()
        self._agents: Dict[ConnectionSettings, AgentState] = dict()

    def get_messages(self) -> Iterable[Message]:
        while not self._recv_queue.empty():
            yield self._recv_queue.get()

    def broadcast(self, message: Message):
        self.send_to(message, None)

    def send_to(self, message: Message, recipient_id: int):
        self._send_queue.put(Payload(message, recipient_id))

    def run(self):
        while not self.requested_stop():
            self._handle_incoming_packet()
            self._handle_outgoing_messages()
            sleep(0.01)

    def _handle_incoming_packet(self):
        packet = self._connection.receive()
        if packet is not None:
            try:
                message = self._to_message(packet.data)
            except Exception:
                return

            sender_address = packet.address
            identifier = message.get_identifier()
            if identifier == 'IMALIVE':
                self._handle_imalive(sender_address)
            elif identifier == 'NETTOPO':
                self._handle_nettopo(message, sender_address)

    def _handle_outgoing_messages(self):
        while not self._send_queue.empty():
            payload: Payload = self._send_queue.get()
            message, recipient_id = payload.message, payload.recipient_id

            recipients = self._get_recipients_by_id(recipient_id)
            self._send(recipients, message)

    def _handle_imalive(self, sender_address: ConnectionSettings):
        self._refresh_agent(sender_address)
        message = NetTopologyMessage(tuple(self._agents.keys()))
        self.send_to(message, hash(sender_address))

    def _handle_nettopo(self,
                        message: NetTopologyMessage,
                        sender_address: ConnectionSettings
                        ):
        addresses = {*message.agents, sender_address}
        for address in addresses:
            self._add_agent(address)

    def _add_agent(self, agent_address: ConnectionSettings):
        if agent_address not in self._agents:
            self._refresh_agent(agent_address)

    def _refresh_agent(self, agent_address: ConnectionSettings):
        self._agents[agent_address] = time()

    def _to_message(self, data: bytes) -> Message:
        return self._message_mapper.map_from_bytes(data)

    def _get_recipients_by_id(self, recipient_id: Optional[int]) -> Iterable[ConnectionSettings]:
        if recipient_id is None:
            return self._agents.keys()
        return {addr for addr in self._agents if hash(addr) == recipient_id}

    def _send(self, recipients: Iterable[ConnectionSettings], message: Message):
        message_as_bytes = self._message_mapper.map_to_bytes(message)
        for recipient in recipients:
            packet = Packet(message_as_bytes, recipient)
            self._connection.send(packet)

    def _create_message_mapper(self) -> MessageMapper:
        return MessageMapper() \
            .register(ImAliveMessage) \
            .register(NetTopologyMessage)
