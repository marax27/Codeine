import string
import itertools
import hashlib
from dataclasses import dataclass
from typing import Dict, Optional, Set
from . import base
from .domain_commands import create_drop_command, create_result_command, create_register_command


@dataclass(frozen=True)
class State(base.State):
    password: str


@dataclass(frozen=True)
class SubproblemId(base.SubproblemId):
    value: str

    def __str__(self) -> str:
        return f'<{self.value}>'

    def __repr__(self) -> str:
        return str(self)


@dataclass(frozen=True)
class SubproblemResult(base.SubproblemResult):
    result: Optional[str]

    def __str__(self) -> str:
        return f'<{self.result}>'

    def __repr__(self) -> str:
        return str(self)


class StopCondition(base.StopCondition):
    def is_met(self, results: Dict[SubproblemId, SubproblemResult]) -> bool:
        return any(r.result is not None for r in results.values())


class SubproblemPool(base.SubproblemPool):
    def _create_initial_pool(self) -> Set[SubproblemResult]:
        prefixes = itertools.product(string.ascii_lowercase + string.digits,
                                     repeat=2)
        return set(map(SubproblemId, map(''.join, prefixes)))


class Subproblem(base.Subproblem):
    def run(self):
        self.result = SubproblemResult(None)
        for suffix in map(''.join, itertools.product(string.ascii_lowercase + string.digits,
                          repeat=4)):
            if self.requested_stop():
                break
            word = self.identifier.value + suffix
            word_byte = word.encode('utf-8')
            hs = hashlib.sha1()
            hs.update(word_byte)
            hs = hs.hexdigest()
            if (hs == self.state.password):
                self.result = SubproblemResult(word)
                break


class ComputationalProblem(base.ComputationalProblem):
    def create_subproblem_pool(self) -> SubproblemPool:
        return SubproblemPool()

    def create_state(self) -> State:
        return State("8c8b31cb137cfa565cc6057b4c4e0e9f04305ac2") #for password "kacpi4"
        #return State("aff975c55e20db44e643411216161ec943cbb0c3") #for password "kacper"

    def create_subproblem(self, identifier: SubproblemId, state: State) -> Subproblem:
        return Subproblem(identifier, state)

    def create_stop_condition(self) -> StopCondition:
        return StopCondition()

    result_command_type: type = create_result_command(SubproblemId,
                                                      SubproblemResult)
    register_command_type: type = create_register_command(SubproblemId)
    drop_command_type: type = create_drop_command(SubproblemId)
