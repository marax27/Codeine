from dataclasses import dataclass
from typing import Set
import app.computing.base as base
from app.computing.domain_commands import create_result_command, create_register_command, create_drop_command, BaseDropCommand, BaseResultCommand
from app.shared.networking import ConnectionSettings

@dataclass(frozen=True)
class TestId(base.SubproblemId):
    identifier: int


@dataclass(frozen=True)
class TestResult(base.SubproblemResult):
    result: int


class TestPool(base.SubproblemPool):
    def _create_initial_pool(self) -> Set[TestResult]:
        return set(TestId(i) for i in range(5))


ResultCommand = create_result_command(TestId, TestResult)
RegisterCommand = create_register_command(TestId)
DropCommand = create_drop_command(TestId)


class ConnectionSettingsFactory:
    @staticmethod
    def higher_priority_address():
        return ConnectionSettings('127.127.127.127', 40000)
    
    @staticmethod
    def lower_priority_address():
        return ConnectionSettings('127.127.127.126', 40000)


def test_resultCommand_invokeUponSamplePool_resultIsInPool():
    given_id = TestId(4)
    given_result = TestResult(999)
    given_command = ResultCommand(given_id, given_result)
    given_pool = TestPool()

    given_command.invoke(given_pool)

    assert given_pool.results[given_id] == given_result
    assert given_id not in given_pool.not_started_pool
    assert given_id not in given_pool.in_progress_pool


def test_resultCommand_invokeUponSubproblemThatAlreadyStarted_resultIsInPool():
    given_id = TestId(4)
    given_result = TestResult(999)
    given_command = ResultCommand(given_id, given_result)
    given_pool = TestPool()
    given_pool.register(given_id)

    given_command.invoke(given_pool)

    assert given_pool.results[given_id] == given_result
    assert given_id not in given_pool.not_started_pool
    assert given_id not in given_pool.in_progress_pool


def test_registerCommand_invokeNoSubproblemBeingComputed_returnsEmptyList():
    given_id = TestId(4)
    given_pool = TestPool()
    given_command = RegisterCommand(given_id)

    register_invoke_output = given_command.invoke(given_pool)

    assert len(register_invoke_output) == 0
    assert given_id in given_pool.in_progress_pool


def test_registerCommand_invokeWithDifferentSubproblemInProgress_returnsEmptyList():
    given_id = TestId(4)
    current_id = TestId(2)
    given_pool = TestPool()
    given_command = RegisterCommand(given_id)
    given_pool.register(current_id)

    register_invoke_output = given_command.invoke(given_pool)

    assert len(register_invoke_output) == 0
    assert given_id in given_pool.in_progress_pool
    assert current_id in given_pool.in_progress_pool


def test_registerCommand_invokeSenderHasGreaterPriority_returnsEmptyList():
    given_id = TestId(4)
    given_pool = TestPool()
    given_command = RegisterCommand(given_id)
    given_pool.register(given_id)

    sender_address = ConnectionSettingsFactory.higher_priority_address()
    local_address = ConnectionSettingsFactory.lower_priority_address()
    given_command.context.initialize(sender_address, local_address)

    register_invoke_output = given_command.invoke(given_pool)

    assert len(register_invoke_output) == 0
    assert given_pool.get_id_in_progress_locally() is None
    assert given_id in given_pool.in_progress_pool


def test_registerCommand_invokeSubproblemInProgressOnDifferentAgent_returnsEmptyList():
    given_id = TestId(4)
    given_pool = TestPool()
    given_command = RegisterCommand(given_id)
    given_pool.register(given_id, ConnectionSettings('1.2.3.4', 9999))

    register_invoke_output = given_command.invoke(given_pool)

    assert len(register_invoke_output) == 0
    assert given_id in given_pool.in_progress_pool


def test_registerCommand_invokeWithSubproblemAlreadyInResults_returnsResult():
    given_id = TestId(4)
    given_result = TestResult(2)
    given_pool = TestPool()
    given_command = RegisterCommand(given_id)
    given_pool.results[given_id] = given_result

    register_invoke_output = given_command.invoke(given_pool)
    
    assert len(register_invoke_output) == 1
    assert isinstance(register_invoke_output[0], BaseResultCommand)
    assert register_invoke_output[0].identifier == given_id
    assert register_invoke_output[0].result == given_result


def test_registerCommand_invokeWithSubproblemInProgress_returnsDrop():
    given_id = TestId(4)
    given_pool = TestPool()
    given_command = RegisterCommand(given_id)
    given_pool.register(given_id)

    sender_address = ConnectionSettingsFactory.lower_priority_address()
    local_address = ConnectionSettingsFactory.higher_priority_address()
    given_command.context.initialize(sender_address, local_address)

    register_invoke_output = given_command.invoke(given_pool)

    assert len(register_invoke_output) == 1
    assert isinstance(register_invoke_output[0], BaseDropCommand)
    assert register_invoke_output[0].identifier == given_id


def test_dropCommand_invokeWithCurrentSubproblemId_currentSubproblemDropped():
    given_id = TestId(4)
    given_pool = TestPool()
    given_command = DropCommand(given_id)
    given_pool.register(given_id)

    given_command.invoke(given_pool)

    assert given_pool.get_id_in_progress_locally() is None


def test_dropCommand_invokeWithDifferentSubproblemId_currentSubproblemNotDropped():
    given_id = TestId(4)
    current_id = TestId(2)
    given_pool = TestPool()
    given_command = DropCommand(given_id)
    given_pool.register(current_id)

    given_command.invoke(given_pool)

    assert given_pool.get_id_in_progress_locally() == current_id


def test_resultCommand_invokeResultOfNotStartedSubproblemReceived_subproblemIsCompleted():
    given_id = TestId(4)
    given_result = TestResult(42)
    given_pool = TestPool()
    given_command = ResultCommand(given_id, given_result)

    given_command.invoke(given_pool)

    assert given_id in given_pool.results
    assert given_pool.results[given_id] == given_result


def test_resultCommand_invokeResultOfInProgressSubproblemReceived_subproblemIsCompleted():
    given_id = TestId(4)
    given_result = TestResult(42)
    given_pool = TestPool()
    given_command = ResultCommand(given_id, given_result)
    given_pool.register(given_id, ConnectionSettings('1.1.1.1', 9999))

    given_command.invoke(given_pool)

    assert given_id in given_pool.results
    assert given_pool.results[given_id] == given_result


def test_resultCommand_invokeResultOfSubproblemBeingComputedReceived_subproblemIsDroppedAndCompleted():
    given_id = TestId(4)
    given_result = TestResult(42)
    given_pool = TestPool()
    given_command = ResultCommand(given_id, given_result)
    given_pool.register(given_id)

    given_command.invoke(given_pool)

    assert given_id in given_pool.results
    assert given_pool.results[given_id] == given_result
    assert given_pool.get_id_in_progress_locally() is None

def test_resultCommand_invokeResultOfSubproblemAlreadyInResultsAndReceivedResultIsDifferent_nothingHappens():
    given_id = TestId(4)
    given_result = TestResult(42)
    current_result = TestResult(16)
    given_pool = TestPool()
    given_command = ResultCommand(given_id, given_result)
    given_pool.register(given_id, ConnectionSettings('1.1.1.1', 9999))
    given_pool.complete(given_id, current_result)

    given_command.invoke(given_pool)

    assert given_id in given_pool.results
    assert given_pool.results[given_id] == current_result
