from dataclasses import dataclass
from dataclasses_json import dataclass_json
from app.computing.base import Subproblem, ComputationalProblem


@dataclass_json
@dataclass(frozen=True)
class ApplicationSettings:
    active_mode: bool


class ComputationManager:
    def __init__(self, problem: ComputationalProblem):
        self._problem = problem
        self._state = problem.create_state()
        self._stop_condition = problem.create_stop_condition()
        self.pool = problem.create_subproblem_pool()

    def create_random(self) -> Subproblem:
        if not self.pool.not_started_pool:
            raise EmptySubproblemPoolError()
        identifier = self.pool.pop_identifier()
        self.pool.register(identifier)
        return self._problem.create_subproblem(identifier, self._state)

    def handle_completed(self, subproblem: Subproblem):
        self.pool.complete(subproblem.identifier, subproblem.result)

    def stop_condition_is_met(self) -> bool:
        return self._stop_condition.is_met(self.pool.results)

    def all_subproblems_finished(self) -> bool:
        return not (self.pool.not_started_pool or self.pool.in_progress_pool)


class EmptySubproblemPoolError(Exception):
    pass
