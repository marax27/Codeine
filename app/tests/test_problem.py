from dataclasses import dataclass
from typing import Set
import pytest
from app.computing import base
from app.computing.problem import Subproblem, State


NUMBER_OF_IDENTIFIERS = 3


@dataclass(frozen=True)
class SampleSubproblemId(base.SubproblemId):
    value: int


@dataclass(frozen=True)
class SampleSubproblemResult(base.SubproblemResult):
    value: str


class SampleStopCondition(base.StopCondition):
    def is_met(self, results: dict) -> bool:
        values = results.values()
        return any(v is not None for v in values)


class SampleSubproblemPool(base.SubproblemPool):
    def _create_initial_pool(self) -> Set[SampleSubproblemId]:
        return set(map(SampleSubproblemId, range(NUMBER_OF_IDENTIFIERS)))


@dataclass(frozen=True)
class ProblemSubproblemId(base.SubproblemId):
    value: str


def test_subproblem_computing_findingAnswerShort():
    answer_id = ProblemSubproblemId("k")
    state = State("aff975c55e20db44e643411216161ec943cbb0c3")
    subproblem = Subproblem(answer_id, state)
    subproblem.run()

    assert subproblem.result.result == 'kacper'


def test_SubproblemPool_creation_expectedElementsInPool():
    given_pool = SampleSubproblemPool()
    first_expected = SampleSubproblemId(0)
    other_expected = SampleSubproblemId(NUMBER_OF_IDENTIFIERS - 1)

    assert first_expected in given_pool.not_started_pool
    assert other_expected in given_pool.not_started_pool


def test_SubproblemPool_popIdentifier_notStartedPoolUnchanged():
    given_pool = SampleSubproblemPool()
    not_started_pool = given_pool.not_started_pool.copy()

    given_pool.pop_identifier()
    assert not_started_pool == given_pool.not_started_pool


def test_SubproblemPool_popIdentifier_inProgressPoolUnchanged():
    given_pool = SampleSubproblemPool()
    in_progress = given_pool.in_progress_pool.copy()

    given_pool.pop_identifier()
    assert in_progress == given_pool.in_progress_pool


def test_SubproblemPool_popIdentifier_resultsUnchanged():
    given_pool = SampleSubproblemPool()
    results = given_pool.results.copy()

    given_pool.pop_identifier()
    assert results == given_pool.results


def test_SubproblemPool_register_poolsChangeAsExpected():
    given_pool = SampleSubproblemPool()

    identifier = given_pool.pop_identifier()
    given_pool.register(identifier)

    assert identifier in given_pool.in_progress_pool
    assert identifier not in given_pool.not_started_pool
    assert identifier not in given_pool.results


def test_revertInProgress_sampleIdentifier_poolsChangeAsExpected():
    given_pool = SampleSubproblemPool()
    identifier = given_pool.pop_identifier()
    given_pool.register(identifier)
    given_pool.revert_in_progress(identifier)

    assert identifier in given_pool.not_started_pool
    assert identifier not in given_pool.in_progress_pool
    assert identifier not in given_pool.results


def test_complete_sampleIdentifier_poolsChangeAsExpected():
    given_pool = SampleSubproblemPool()
    given_result = SampleSubproblemResult('sample')

    identifier = given_pool.pop_identifier()
    given_pool.register(identifier)
    given_pool.complete(identifier, given_result)

    assert identifier not in given_pool.not_started_pool
    assert identifier not in given_pool.in_progress_pool
    assert identifier in given_pool.results


@pytest.mark.parametrize('given_results,expected_is_met', (
    ({1: None, 2: None, 3: 'x'}, True),
    ({1: 'x', 2: None, 3: None}, True),
    ({1: None, 2: None, 3: None}, False),
    ({}, False),
    ({1: 'x'}, True),
    ({1: 'x', 2: 'y'}, True)
))
def test_isMet_sampleResults_meetExpectation(given_results, expected_is_met):
    stop_condition = SampleStopCondition()
    assert stop_condition.is_met(given_results) == expected_is_met
