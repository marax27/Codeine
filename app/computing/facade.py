from .computing import Task, TaskIdentifier
from .state import StateFactory


class TaskPool:
    def __init__(self):
        raise NotImplementedError()

    def pop_identifier(self) -> TaskIdentifier:
        raise NotImplementedError()


class TaskFactory:
    def __init__(self):
        state_factory = StateFactory()
        self._state = state_factory.create()

    def create(self, identifier: TaskIdentifier) -> Task:
        return Task(identifier, self._state)
