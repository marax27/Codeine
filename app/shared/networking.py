import socket
from dataclasses import dataclass
from typing import Optional
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True)
class ConnectionSettings:
    address: str
    port: int

    @staticmethod
    def from_tuple(address_info: tuple):
        return ConnectionSettings(address_info[0], address_info[1])

    def to_tuple(self) -> tuple:
        return (self.address, self.port)


@dataclass(frozen=True)
class Packet:
    data: bytes
    address: ConnectionSettings


class SendError(Exception):
    pass


class ReadError(Exception):
    pass


class NetworkConnection:
    '''Wrapper for low-level socket operations.'''

    def __init__(self, connection_settings: ConnectionSettings):
        self._connection_settings = connection_settings
        self._socket = self._create_socket()
        self._bind_socket()

    def __del__(self):
        if self._socket:
            self._socket.close()

    def send(self, packet: Packet):
        try:
            connection_address = packet.address.to_tuple()
            self._socket.sendto(packet.data, connection_address)
        except OSError as exc:
            raise SendError(exc)

    def receive(self) -> Optional[Packet]:
        try:
            data, address = self._socket.recvfrom(65536)
            return Packet(data, ConnectionSettings.from_tuple(address))
        except BlockingIOError:
            return None
        except OSError as exc:
            raise ReadError(exc.errno)

    def _bind_socket(self):
        self._socket.bind(self._connection_settings.to_tuple())

    def _create_socket(self) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setblocking(False)
        return sock
