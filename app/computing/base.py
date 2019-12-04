import random
from abc import ABC, abstractmethod
from threading import Thread
from typing import Optional, Set
from app.shared.multithreading import StoppableThread


class State(ABC):
    pass


class TaskIdentifier(ABC):
    pass


class TaskResult(ABC):
    pass


class TaskPool(ABC):
    def __init__(self):
        self.not_started_pool = self._create_initial_pool()
        self.in_progress_pool = set()
        self.results = dict()

    @abstractmethod
    def _create_initial_pool(self) -> Set[TaskIdentifier]:
        pass

    def pop_identifier(self) -> TaskIdentifier:
        return random.choice(tuple(self.not_started_pool))

    def register(self, identifier: TaskIdentifier):
        self.not_started_pool.remove(identifier)
        self.in_progress_pool.add(identifier)

    def revert_in_progress(self, identifier: TaskIdentifier):
        self.in_progress_pool.remove(identifier)
        self.not_started_pool.add(identifier)

    def complete(self, identifier: TaskIdentifier, result: TaskResult):
        self.in_progress_pool.remove(identifier)
        if identifier not in self.results:
            self.results[identifier] = result


class Task(StoppableThread, ABC):
    def __init__(self, identifier: TaskIdentifier, state: State):
        super().__init__()
        self.identifier = identifier
        self.state = state
        self.result: Optional[TaskResult] = None

    @abstractmethod
    def run(self):
        pass


class ComputationalProblem(ABC):
    @abstractmethod
    def create_state(self) -> State:
        pass

    @abstractmethod
    def create_task_pool(self) -> TaskPool:
        pass

    @abstractmethod
    def create_task(self, identifier: TaskIdentifier, state: State) -> Task:
        pass
