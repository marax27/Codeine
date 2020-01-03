import random
from abc import ABC, abstractmethod
from typing import Optional, Set
from app.shared.multithreading import StoppableThread


class State(ABC):
    pass


class SubproblemId(ABC):
    pass


class SubproblemResult(ABC):
    pass


class SubproblemPool(ABC):
    def __init__(self):
        self.not_started_pool = self._create_initial_pool()
        self.in_progress_pool = set()
        self.results = dict()
        self.current_subproblem_id: SubproblemId = None

    @abstractmethod
    def _create_initial_pool(self) -> Set[SubproblemId]:
        pass

    def pop_identifier(self) -> SubproblemId:
        return random.choice(tuple(self.not_started_pool))

    def register(self, identifier: SubproblemId):
        self.not_started_pool.remove(identifier)
        self.in_progress_pool.add(identifier)

    def revert_in_progress(self, identifier: SubproblemId):
        self.in_progress_pool.remove(identifier)
        self.not_started_pool.add(identifier)

    def signal_subproblem_stop(self):
        self.current_subproblem_id = None

    def complete(self, identifier: SubproblemId, result: SubproblemResult):
        self.in_progress_pool.remove(identifier)
        self.signal_subproblem_stop()
        if identifier not in self.results:
            self.results[identifier] = result


class Subproblem(StoppableThread):
    def __init__(self, identifier: SubproblemId, state: State):
        super().__init__()
        self.identifier = identifier
        self.state = state
        self.result: Optional[SubproblemResult] = None

    @abstractmethod
    def run(self):
        pass


class ComputationalProblem(ABC):
    @abstractmethod
    def create_state(self) -> State:
        pass

    @abstractmethod
    def create_subproblem_pool(self) -> SubproblemPool:
        pass

    @abstractmethod
    def create_subproblem(self, identifier: SubproblemId, state: State) -> Subproblem:
        pass

    result_command_type: type
    register_command_type: type
    drop_command_type: type
