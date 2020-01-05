import pytest

from app.shared.time import TimeoutService
from app.messaging.topology import Topology, NetTopologyCommand, ImAliveCommand, RecipientNotRegisteredError
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


class TimeProviderMock(TimeoutService):
    def __init__(self, timeout_threshold: float):
        super().__init__(timeout_threshold)
        self.current_time = 0.0

    def set_time(self, value: float):
        self.current_time = value

    def now(self) -> float:
        return self.current_time


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


def test_addOrUpdate_sampleAddress_addressPresentInReturnedAddresses():
    given_address = ConnectionSettings('1.2.3.4', 1234)
    sut = Topology(TimeoutService(123))

    sut.add_or_update(given_address)
    assert given_address in sut.get_all_addresses()


def test_addOrUpdateMany_sampleAddresses_initialAndReturnedAddressesAreEqual():
    given_addresses = [
        ConnectionSettings('1.2.3.4', 1000),
        ConnectionSettings('1.2.3.5', 2000)
    ]
    sut = Topology(TimeoutService(123))

    sut.add_or_update_many(given_addresses)
    assert set(sut.get_all_addresses()) == set(given_addresses)


def test_withForbidden_addForbiddenAddress_addressNotAdded():
    given_address = ConnectionSettings('1.2.3.4', 1000)
    sut = Topology(TimeoutService(123)).with_forbidden(given_address)
    assert given_address not in sut.get_all_addresses()


def test_getAddresses_sampleTopology_iterableWithGivenTopology():
    given_address = ConnectionSettings('1.2.3.4', 1000)
    sut = Topology(TimeoutService(123))

    sut.add_or_update(given_address)
    assert given_address in sut.get_addresses(given_address)


def test_getAddresses_unexpectedTopology_raise():
    given_address = ConnectionSettings('1.2.3.4', 1000)
    sut = Topology(TimeoutService(123))

    with pytest.raises(RecipientNotRegisteredError):
        sut.get_addresses(given_address)


def test_getAddresses_none_allRegisteredAddresses():
    given_addresses = [
        ConnectionSettings('1.2.3.4', 1000),
        ConnectionSettings('1.2.3.5', 2000)
    ]

    sut = Topology(TimeoutService(123))
    sut.add_or_update_many(given_addresses)

    assert all(addr in sut.get_addresses(None) for addr in given_addresses)


def test_prune_sampleTopology_expectedAgentsAreReturnedFromPruned():
    '''This test verifies values returned from prune().'''

    given_addresses = [
        ConnectionSettings('1.1.1.1', 1234),
        ConnectionSettings('1.1.1.2', 1234),
        ConnectionSettings('1.1.1.3', 1234)
    ]
    given_timeout = 5.0

    time_provider = TimeProviderMock(given_timeout)
    sut = Topology(time_provider)

    time_provider.set_time(0.0)
    sut.add_or_update_many(given_addresses)

    time_provider.set_time(2.5)
    sut.add_or_update(given_addresses[0])

    time_provider.set_time(5.0)
    pruned_agents = sut.prune()

    assert set(pruned_agents) == {given_addresses[1], given_addresses[2]}


def test_prune_sampleTopology_expectedAgentsAreRemovedFromTopology():
    '''This test verifies if agents are actually removed from a topology.'''

    given_addresses = [
        ConnectionSettings('1.1.1.1', 1234),
        ConnectionSettings('1.1.1.2', 1234),
        ConnectionSettings('1.1.1.3', 1234)
    ]
    given_timeout = 5.0

    time_provider = TimeProviderMock(given_timeout)
    sut = Topology(time_provider)

    time_provider.set_time(0.0)
    sut.add_or_update_many(given_addresses)

    time_provider.set_time(2.5)
    sut.add_or_update(given_addresses[0])

    time_provider.set_time(5.0)
    _ = sut.prune()

    all_addresses = set(sut.get_all_addresses())
    assert all_addresses == {given_addresses[0]}
