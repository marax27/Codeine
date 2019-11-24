from dataclasses import dataclass
from threading import Thread
from typing import Optional

from .state import State


@dataclass(frozen=True)
class TaskIdentifier:
    value: str


@dataclass(frozen=True)
class TaskResult:
    result: Optional[str]


class Task(Thread):
    def __init__(self, identifier: TaskIdentifier, state: State):
        super().__init__()
        self._identifier = identifier
        self._state = state
        self.result: Optional[TaskResult] = None

    def run(self):
        pass
