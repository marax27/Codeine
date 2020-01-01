from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable, Optional
from .commands import Command
from ..computing.base import SubproblemPool, SubproblemId, SubproblemResult


class DomainCommand(Command):

    @abstractmethod
    def invoke(self, receiver: SubproblemPool) -> Iterable[Command]:
        pass


@dataclass(frozen=True)
class SubproblemResultCommand(DomainCommand):
    identifier: SubproblemId
    result: Optional[SubproblemResult]

    @classmethod
    def get_identifier(cls) -> str:
        return 'SUBPROBRES'

    def invoke(self, receiver: SubproblemPool) -> Iterable[Command]:
        pass
