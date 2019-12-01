import string
import itertools
import hashlib
from dataclasses import dataclass
from typing import Optional, Set
from . import base


@dataclass(frozen=True)
class State(base.State):
    password: bytes


@dataclass(frozen=True)
class TaskIdentifier(base.TaskIdentifier):
    value: str


@dataclass(frozen=True)
class TaskResult(base.TaskResult):
    result: Optional[str]


class TaskPool(base.TaskPool):
    def _create_initial_pool(self) -> Set[TaskResult]:
        prefixes = itertools.product(string.ascii_lowercase, repeat=2)
        return set(map(TaskIdentifier, map(''.join, prefixes)))


class Task(base.Task):
    def run(self):
        a = 0
        b = 0
        c = 0
        d = 0
        for i in range(26**4):
            if (a == 26):
                a = 0
                b += 1
            if (b == 26):
                b = 0
                c += 1
            if (c == 26):
                c = 0
                d = +1
            word = self.identifier.value + chr(a+97) + chr(b+97) + chr(c+97) + chr(d+97)
            a = a+1
            word_byte = word.encode('utf-8')
            hs = hashlib.sha1()
            hs.update(word_byte)
            hs = hs.digest()
            if (hs == self.state.password):
                self.result = TaskResult(word)
        
        
class ComputationalProblem(base.ComputationalProblem):
    def create_task_pool(self) -> TaskPool:
        return TaskPool()

    def create_state(self) -> State:
        return State(b'(\xb75K[\xff\xcbqN\xb0v9\xd5@W\r\xe6\xf2+\xf0')

    def create_task(self, identifier: TaskIdentifier, state: State) -> Task:
        return Task(identifier, state)
