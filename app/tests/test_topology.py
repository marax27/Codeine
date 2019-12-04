import pytest

from app.messaging.topology import NetTopologyCommand, ImAliveCommand
from app.messaging.commands import CommandMapper
from app.shared.networking import ConnectionSettings


class NetTopologyCommandFactory:
    @staticmethod
    def create() -> NetTopologyCommand:
        network_connection_1 = ConnectionSettings('192.168.192.1', 2137)
        network_connection_2 = ConnectionSettings('192.168.192.2', 2137)
        agents = (network_connection_1, network_connection_2)
        command = NetTopologyCommand(agents)
        return command


class MapperFactory:
    @staticmethod
    def create(type_to_register: type) -> CommandMapper:
        return CommandMapper().register(type_to_register)


def test_nettopologyMapping_sampleCommand_commandMappedCorrectly():
    command = NetTopologyCommandFactory().create()

    mapper = MapperFactory().create(NetTopologyCommand)
    command_as_bytes = mapper.map_to_bytes(command)
    command_from_bytes = mapper.map_from_bytes(command_as_bytes)

    assert command_from_bytes == command


def test_imaliveMapping_sampleCommand_commandMappedCorrectly():
    command = ImAliveCommand()
    mapper = MapperFactory().create(ImAliveCommand)

    command_as_bytes = mapper.map_to_bytes(command)
    command_from_bytes = mapper.map_from_bytes(command_as_bytes)

    assert command_from_bytes == command


def test_imaliveMapping_sampleCommand_byteCommandContainsCommandId():
    command = ImAliveCommand()
    command_id = command.get_identifier()
    mapper = CommandMapper().register(ImAliveCommand)

    command_as_bytes = mapper.map_to_bytes(command)

    assert command_id.encode('UTF-8') in command_as_bytes


def test_imaliveMapping_sampleCommand_byteCommandContainsEmptyBrackets():
    command = ImAliveCommand()
    mapper = MapperFactory().create(ImAliveCommand)

    command_as_bytes = mapper.map_to_bytes(command)

    assert b'{}' in command_as_bytes
