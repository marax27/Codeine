from dataclasses import dataclass
from dataclasses_json import dataclass_json
from app.computing.base import Subproblem, ComputationalProblem
from .messaging.broker import Broker
from app.messaging.domain_commands import SubproblemResultCommand


@dataclass_json
@dataclass(frozen=True)
class ApplicationSettings:
    active_mode: bool


class ComputationManager:
    def __init__(self, problem: ComputationalProblem):
        self._problem = problem
        self._state = problem.create_state()
        self.pool = problem.create_subproblem_pool()

    def create_random(self) -> Subproblem:
        if not self.pool.not_started_pool:
            raise EmptySubproblemPoolError()
        identifier = self.pool.pop_identifier()
        self.pool.register(identifier)
        return self._problem.create_subproblem(identifier, self._state)

    def handle_completed(self, subproblem: Subproblem):
        self.pool.complete(subproblem.identifier, subproblem.result)

    def all_subproblems_finished(self) -> bool:
        return not (self.pool.not_started_pool or self.pool.in_progress_pool)

    def broadcast_result(self, subproblem: Subproblem, broker: Broker):
        command = SubproblemResultCommand(subproblem.identifier, subproblem.result)
        broker.broadcast(command)


class EmptySubproblemPoolError(Exception):
    pass
