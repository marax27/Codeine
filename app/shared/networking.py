import socket
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from dataclasses_json import dataclass_json
from ifaddr import get_adapters


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

    def get_priority(self) -> int:
        data = bytes(map(int, self.address.split('.')))
        data += (self.port).to_bytes(2, 'big')
        return int.from_bytes(data, byteorder='big', signed=False)

    def __repr__(self) -> str:
        return f'<{self.address}:{self.port}>'


@dataclass(frozen=True)
class Packet:
    data: bytes
    address: ConnectionSettings


class SendError(Exception):
    pass


class ReadError(Exception):
    pass


class NetworkIO(ABC):
    @abstractmethod
    def send(self, packet: Packet):
        pass

    @abstractmethod
    def receive(self) -> Optional[Packet]:
        pass

    @abstractmethod
    def get_address(self) -> ConnectionSettings:
        pass


class NetworkConnection(NetworkIO):
    '''Wrapper for low-level socket operations.'''

    def __init__(self, connection_settings: ConnectionSettings):
        self._connection_settings = connection_settings
        self._socket = self._create_socket()
        self._bind_socket()

    def __del__(self):
        if self._socket:
            self._socket.close()

    def get_address(self) -> ConnectionSettings:
        return self._connection_settings

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


def get_local_interfaces_addresses() -> List[str]:
    adapters = get_adapters()
    addresses_per_adapter = [[x.ip for x in a.ips] for a in adapters]
    all_addresses = [ip for sublist in addresses_per_adapter for ip in sublist]
    return list(filter(lambda ip: isinstance(ip, str), all_addresses))
