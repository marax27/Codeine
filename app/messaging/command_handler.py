from __future__ import annotations
from typing import Any, Dict, Iterable, Optional
from dataclasses import dataclass
from app.shared.networking import ConnectionSettings
from .commands import Command


@dataclass(frozen=True)
class Payload:
    '''Command + information where to send it.'''
    command: Command
    address: Optional[ConnectionSettings]


class CommandHandler:
    def __init__(self):
        self._registered_types: Dict[type, Any] = dict()

    def register(self, command_type: type, receiver: Any) -> CommandHandler:
        if receiver is None:
            raise NoneReceiverException(command_type)
        self._registered_types[command_type] = receiver
        return self

    def handle(self, payload: Payload) -> Iterable[Payload]:
        command, address = payload.command, payload.address

        receiver = self._get_receiver(command)
        responses = command.invoke(receiver)
        if responses:
            for response in responses:
                yield Payload(response, address)

    def _get_receiver(self, command: Command) -> Optional[Any]:
        for registered_type, receiver in self._registered_types.items():
            if isinstance(command, registered_type):
                return receiver
        raise CommandNotRegisteredException(command)


class NoneReceiverException(Exception):
    pass


class CommandNotRegisteredException(Exception):
    pass
