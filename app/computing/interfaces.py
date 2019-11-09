from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class IState(ABC):
    pass


@dataclass(frozen=True)
class ITaskResult(ABC):
    pass


@dataclass(frozen=True)
class ITaskIdentifier(ABC):
    pass


class ITaskIdentifierPool(ABC):
    @abstractmethod
    def pop_random_identifier(self) -> ITaskIdentifier:
        pass


class ITask(ABC):
    def __init__(self, identifier: ITaskIdentifier, state: IState):
        self._id = identifier
        self._state = state

    @abstractmethod
    def run(self) -> ITaskResult:
        pass


class ITaskFactory:
    def __init__(self, state: IState):
        self._state = state

    @abstractmethod
    def create(self, identifier: ITaskIdentifier) -> ITask:
        pass
