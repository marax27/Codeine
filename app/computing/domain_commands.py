from abc import abstractmethod
from dataclasses import dataclass, make_dataclass
from typing import Iterable, Optional
from app.messaging.commands import Command
import app.computing.base as base


class DomainCommand(Command):
    @abstractmethod
    def invoke(self, receiver: base.SubproblemPool) -> Iterable[Command]:
        pass


@dataclass(frozen=True)
class BaseResultCommand(DomainCommand):
    identifier: base.SubproblemId
    result: Optional[base.SubproblemResult]

    @classmethod
    def get_identifier(cls) -> str:
        return 'RESULT'

    def invoke(self, receiver: base.SubproblemPool) -> Iterable[Command]:
        pass


def create_result_command(identifier_type: type, result_type: type) -> type:
    return make_dataclass(
        'ResultCommand',
        (('identifier', identifier_type), ('result', result_type)),
        bases=(BaseResultCommand,),
        frozen=True
    )
