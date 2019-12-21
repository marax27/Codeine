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
    result: Optional[str]


class TaskPool(base.TaskPool):
    def _create_initial_pool(self) -> Set[TaskResult]:
        prefixes = itertools.product(string.ascii_lowercase, 
                                     repeat=1)
        return set(map(TaskIdentifier, map(''.join, prefixes)))


class Task(base.Task):
    def run(self):
        for suffix in map(''.join, itertools.product(string.ascii_lowercase,
                          repeat=5)):
            if not self.requested_stop():
                word = self.identifier.value + suffix
                word_byte = word.encode('utf-8')
                hs = hashlib.sha1()
                hs.update(word_byte)
                hs = hs.hexdigest()
                if (hs == self.state.password):
                    self.result = TaskResult(word)
                    break


class ComputationalProblem(base.ComputationalProblem):
    def create_task_pool(self) -> TaskPool:
        return TaskPool()

    def create_state(self) -> State:
        #return State("8c8b31cb137cfa565cc6057b4c4e0e9f04305ac2") #for password "kacpi4"
        return State("aff975c55e20db44e643411216161ec943cbb0c3") #for password "kacper"

    def create_task(self, identifier: TaskIdentifier, state: State) -> Task:
        return Task(identifier, state)
