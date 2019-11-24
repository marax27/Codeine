from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    password: str


class StateFactory:
    def create(self) -> State:
        raise NotImplementedError()
