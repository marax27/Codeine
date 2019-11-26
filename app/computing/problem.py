import string
import itertools
from dataclasses import dataclass
from typing import Optional, Set
from . import base


@dataclass(frozen=True)
class State(base.State):
    password: str


@dataclass(frozen=True)
class TaskIdentifier(base.TaskIdentifier):
    value: str


@dataclass(frozen=True)
class TaskResult(base.TaskResult):
    result: Optional[str]


class TaskPool(base.TaskPool):
    def _create_initial_pool(self) -> Set[TaskResult]:
        prefixes = itertools.product(string.ascii_lowercase, repeat=3)
        return set(map(TaskIdentifier, map(''.join, prefixes)))


class Task(base.Task):
    def run(self):
        raise NotImplementedError()


class ComputationalProblem(base.ComputationalProblem):
    def create_task_pool(self) -> TaskPool:
        return TaskPool()

    def create_state(self) -> State:
        return State('SamplePassword')

    def create_task(self, identifier: TaskIdentifier, state: State) -> Task:
        return Task(identifier, state)
