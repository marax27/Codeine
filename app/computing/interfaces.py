from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class State(ABC):
    pass


@dataclass(frozen=True)
class TaskResult(ABC):
    pass


@dataclass(frozen=True)
class TaskIdentifier(ABC):
    pass


class TaskIdentifierPool(ABC):
    @abstractmethod
    def pop_random_identifier(self) -> TaskIdentifier:
        pass


class Task(ABC):
    def __init__(self, identifier: TaskIdentifier, state: State):
        self._id = identifier
        self._state = state

    @abstractmethod
    def run(self) -> TaskResult:
        pass


class TaskFactory:
    def __init__(self, state: State):
        self._state = state

    @abstractmethod
    def create(self, identifier: TaskIdentifier) -> Task:
        pass
