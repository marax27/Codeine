from dataclasses import dataclass
from typing import Set
import pytest
from app.computing.base import TaskPool, TaskIdentifier, TaskResult
from app.computing.problem import Task, State


NUMBER_OF_IDENTIFIERS = 3


@dataclass(frozen=True)
class SampleTaskIdentifier(TaskIdentifier):
    value: int


@dataclass(frozen=True)
class SampleTaskResult(TaskResult):
    value: str


class SampleTaskPool(TaskPool):
    def _create_initial_pool(self) -> Set[SampleTaskIdentifier]:
        return set(map(SampleTaskIdentifier, range(NUMBER_OF_IDENTIFIERS)))

@dataclass(frozen=True)
class ProblemTaskIdentifier(TaskIdentifier):
    value: str  


def test_task_computing_findingAnswerShort():
    answer_id = ProblemTaskIdentifier("mr")
    state = State(b'(\xb75K[\xff\xcbqN\xb0v9\xd5@W\r\xe6\xf2+\xf0')
    task = Task(answer_id, state)
    task.run()

    assert task.result.result == 'mrowka'



def test_taskPool_creation_expectedElementsInPool():
    given_pool = SampleTaskPool()
    first_expected = SampleTaskIdentifier(0)
    other_expected = SampleTaskIdentifier(NUMBER_OF_IDENTIFIERS - 1)

    assert first_expected in given_pool.not_started_pool
    assert other_expected in given_pool.not_started_pool


def test_taskPool_popIdentifier_notStartedPoolUnchanged():
    given_pool = SampleTaskPool()
    not_started_pool = given_pool.not_started_pool.copy()

    given_pool.pop_identifier()
    assert not_started_pool == given_pool.not_started_pool


def test_taskPool_popIdentifier_inProgressPoolUnchanged():
    given_pool = SampleTaskPool()
    in_progress = given_pool.in_progress_pool.copy()

    given_pool.pop_identifier()
    assert in_progress == given_pool.in_progress_pool


def test_taskPool_popIdentifier_resultsUnchanged():
    given_pool = SampleTaskPool()
    results = given_pool.results.copy()

    given_pool.pop_identifier()
    assert results == given_pool.results


def test_taskPool_register_poolsChangeAsExpected():
    given_pool = SampleTaskPool()

    identifier = given_pool.pop_identifier()
    given_pool.register(identifier)

    assert identifier in given_pool.in_progress_pool
    assert identifier not in given_pool.not_started_pool
    assert identifier not in given_pool.results


def test_revertInProgress_sampleIdentifier_poolsChangeAsExpected():
    given_pool = SampleTaskPool()
    identifier = given_pool.pop_identifier()
    given_pool.register(identifier)
    given_pool.revert_in_progress(identifier)

    assert identifier in given_pool.not_started_pool
    assert identifier not in given_pool.in_progress_pool
    assert identifier not in given_pool.results


def test_complete_sampleIdentifier_poolsChangeAsExpected():
    given_pool = SampleTaskPool()
    given_result = SampleTaskResult('sample')

    identifier = given_pool.pop_identifier()
    given_pool.register(identifier)
    given_pool.complete(identifier, given_result)

    assert identifier not in given_pool.not_started_pool
    assert identifier not in given_pool.in_progress_pool
    assert identifier in given_pool.results
