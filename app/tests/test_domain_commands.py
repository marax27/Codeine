from dataclasses import dataclass
from typing import Set
import app.computing.base as base
from app.computing.domain_commands import create_result_command


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


def test_resultCommand_invokeUponSamplePool_resultIsInPool():
    given_id = TestId(4)
    given_result = TestResult(999)
    given_command = ResultCommand(given_id, given_result)
    given_pool = TestPool()

    given_command.invoke(given_pool)

    assert given_pool.results[given_id] == given_result
