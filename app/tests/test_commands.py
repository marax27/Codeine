from typing import List, Tuple
from dataclasses import dataclass
import pytest

from app.messaging.commands import Command, CommandMapper, CommandTypeNotRegisteredError


@dataclass(frozen=True)
class SampleCommand(Command):
    identifier: int
    values: Tuple[Tuple[int, int], ...]

    @classmethod
    def get_identifier(cls) -> str:
        return 'SAMPLECMD'

    def invoke(self, _) -> List[Command]:
        return []


class CommandFactory:
    @staticmethod
    def sample() -> Command:
        return SampleCommand(42, ((1, 2),))

    @staticmethod
    def other() -> Command:
        return SampleCommand(55, ((1, 2),))


class MapperFactory:
    @staticmethod
    def create() -> CommandMapper:
        return CommandMapper().register(SampleCommand)


def test_commandCreation_sampleCommand_expectedIdentifier():
    given_command = CommandFactory.sample()
    assert given_command.get_identifier() == 'SAMPLECMD'


def test_mapToBytes_sampleCommand_expectedBytes():
    given_command = CommandFactory.sample()
    given_mapper = MapperFactory.create()

    data = given_mapper.map_to_bytes(given_command)
    assert data == b'SAMPLECMD{"identifier": 42, "values": [[1, 2]]}'


def test_mapToBytes_unregisteredCommandraise():
    given_command = CommandFactory.sample()
    given_mapper = CommandMapper()

    with pytest.raises(CommandTypeNotRegisteredError):
        given_mapper.map_to_bytes(given_command)


def test_mapFromBytes_jsonArray_convertToTuple():
    given_bytes = b'SAMPLECMD{"identifier": 1, "values": [[5, 5], [6, 6]]}'
    given_mapper = MapperFactory.create()

    actual_command: SampleCommand = given_mapper.map_from_bytes(given_bytes)
    assert isinstance(actual_command.values, tuple)
    assert isinstance(actual_command.values[0], tuple)


def test_mapFromBytes_sampleBytes_expectedCommand():
    given_bytes = b'SAMPLECMD{"identifier": 1, "values": [[5, 5], [6, 6]]}'
    given_mapper = MapperFactory.create()

    expected_command = SampleCommand(1, ((5, 5), (6, 6)))
    actual_command = given_mapper.map_from_bytes(given_bytes)
    assert expected_command == actual_command


def test_mapFromBytes_unregisteredCommand_raise():
    given_bytes = b'UNREGISTERED{"sample": 123}'
    given_mapper = MapperFactory.create()

    with pytest.raises(CommandTypeNotRegisteredError):
        given_mapper.map_from_bytes(given_bytes)
