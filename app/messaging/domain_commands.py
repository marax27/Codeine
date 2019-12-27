from abc import abstractmethod
from typing import Iterable, ClassVar, Optional
from .commands import Command
from ..computing.base import SubproblemPool, SubproblemId, SubproblemResult
from .commands import CommandDestination, Broadcast

class DomainCommand(Command):

    @abstractmethod
    def invoke(self, receiver: SubproblemPool) -> Iterable[Command]:
        pass


class SubproblemResultCommand(DomainCommand):
    def __init__(self, subtask: SubproblemId, result: SubproblemResult):
        subtask: SubproblemId
        result: Optional[SubproblemResult]
        response_destination: ClassVar[CommandDestination] = Broadcast()

    @classmethod
    def get_identifier(cls) -> str:
        return 'SUBPROBRES'

    def invoke(self, receiver: SubproblemPool) -> Iterable[Command]:
        pass