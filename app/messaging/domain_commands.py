from abc import abstractmethod
from typing import Iterable, ClassVar, Optional
from .commands import Command
from ..computing.base import SubproblemPool, SubproblemId, SubproblemResult
from dataclasses import dataclass

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