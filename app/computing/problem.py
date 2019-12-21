import string
import itertools
import hashlib
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
    result: Optional[str] = None


class TaskPool(base.TaskPool):
    def _create_initial_pool(self) -> Set[TaskResult]:
        prefixes = itertools.product(string.ascii_lowercase + string.digits,
                                     repeat=2)
        return set(map(TaskIdentifier, map(''.join, prefixes)))


class Task(base.Task):
    def run(self):
        for suffix in map(''.join, itertools.product(string.ascii_lowercase +
                          string.digits, repeat=4)):
            if not self.requested_stop():
                word = self.identifier.value + suffix
                word_byte = word.encode('utf-8')
                hs = hashlib.sha1()
                hs.update(word_byte)
                hs = hs.hexdigest()
                if (hs == self.state.password):
                    self.result .result = word
                    break


class ComputationalProblem(base.ComputationalProblem):
    def create_task_pool(self) -> TaskPool:
        return TaskPool()

    def create_state(self) -> State:
        return State("8c8b31cb137cfa565cc6057b4c4e0e9f04305ac2")

    def create_task(self, identifier: TaskIdentifier, state: State) -> Task:
        return Task(identifier, state)
