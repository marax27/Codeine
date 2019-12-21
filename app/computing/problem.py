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
class SubproblemId(base.SubproblemId):
    value: str


@dataclass(frozen=True)
class SubproblemResult(base.SubproblemResult):
    result: Optional[str]


class SubproblemPool(base.SubproblemPool):
    def _create_initial_pool(self) -> Set[SubproblemResult]:
        prefixes = itertools.product(string.ascii_lowercase,
                                     repeat=1)
        return set(map(SubproblemId, map(''.join, prefixes)))


class Subproblem(base.Subproblem):
    def run(self):
        for suffix in map(''.join, itertools.product(string.ascii_lowercase,
                          repeat=5)):
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
        #return State("8c8b31cb137cfa565cc6057b4c4e0e9f04305ac2") #for password "kacpi4"
        return State("aff975c55e20db44e643411216161ec943cbb0c3") #for password "kacper"

    def create_subproblem(self, identifier: SubproblemId, state: State) -> Subproblem:
        return Subproblem(identifier, state)
