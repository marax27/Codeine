import socket
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ConnectionSettings:
    address: str
    port: int

    @staticmethod
    def from_tuple(address_info: tuple):
        return ConnectionSettings(address_info[0], address_info[1])

    def to_tuple(self) -> tuple:
        return (self.address, self.port)


class SendError(Exception):
    pass


class ReadError(Exception):
    pass


class NetworkConnection:
    '''Wrapper for low-level socket operations.'''

    def __init__(self, connection_settings: ConnectionSettings):
        self._connection_settings = connection_settings
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._bind_socket()

    def __del__(self):
        if self._socket:
            self._socket.close()

    def send(self, data: bytes, connection_settings: ConnectionSettings):
        try:
            self._socket.sendto(data, connection_settings.to_tuple())
        except OSError as exc:
            raise SendError(exc)

    def receive(self) -> Tuple[bytes, ConnectionSettings]:
        try:
            data, address = self._socket.recvfrom(65536)
            return data, ConnectionSettings.from_tuple(address)
        except OSError as exc:
            raise ReadError(exc)

    def _bind_socket(self):
        self._socket.bind(self._connection_settings.to_tuple())
