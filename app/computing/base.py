import random
from abc import ABC, abstractmethod
from typing import Dict, Optional, Set
from app.shared.multithreading import StoppableThread
from app.shared.networking import ConnectionSettings


class State(ABC):
    pass


class SubproblemId(ABC):
    pass


class SubproblemResult(ABC):
    pass


class StopCondition(ABC):
    @abstractmethod
    def is_met(self, results: Dict[SubproblemId, SubproblemResult]) -> bool:
        pass


class SubproblemPool(ABC):
    def __init__(self):
        self.not_started_pool = self._create_initial_pool()
        self.in_progress_pool = dict()
        self.results = dict()

    @abstractmethod
    def _create_initial_pool(self) -> Set[SubproblemId]:
        pass

    def pop_identifier(self) -> SubproblemId:
        return random.choice(tuple(self.not_started_pool))

    def register(self, identifier: SubproblemId, address: ConnectionSettings = None):
        self.not_started_pool.remove(identifier)
        self.update_worker_address(identifier, address)

    def revert_in_progress(self, identifier: SubproblemId):
        self.in_progress_pool.pop(identifier)
        self.not_started_pool.add(identifier)

    def complete(self, identifier: SubproblemId, result: SubproblemResult):
        self.in_progress_pool.pop(identifier)
        if identifier not in self.results:
            self.results[identifier] = result

    def update_worker_address(self, identifier: SubproblemId, address: ConnectionSettings):
        self.in_progress_pool[identifier] = address

    def signal_local_subproblem_stop(self):
        identifier = self.get_id_in_progress_locally()
        self.in_progress_pool.pop(identifier)

    def get_id_in_progress_locally(self) -> Optional[SubproblemId]:
        ids = [k for k, addr in self.in_progress_pool.items() if addr is None]
        assert len(ids) <= 1
        return ids[0] if ids else None


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

    @abstractmethod
    def create_stop_condition(self) -> StopCondition:
        pass

    result_command_type: type
    register_command_type: type
    drop_command_type: type
