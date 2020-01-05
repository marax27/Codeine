from abc import abstractmethod
from dataclasses import dataclass, make_dataclass
from typing import List, Optional
from app.shared.networking import ConnectionSettings
from app.messaging.commands import Command
import app.computing.base as base


class DomainCommand(Command):
    @abstractmethod
    def invoke(self, receiver: base.SubproblemPool) -> List[Command]:
        pass


@dataclass(frozen=True)
class BaseResultCommand(DomainCommand):
    identifier: base.SubproblemId
    result: Optional[base.SubproblemResult]

    @classmethod
    def get_identifier(cls) -> str:
        return 'RESULT'

    def invoke(self, receiver: base.SubproblemPool) -> List[Command]:
        if self.identifier not in receiver.results:
            if self.identifier not in receiver.in_progress_pool:
                receiver.register(self.identifier)
            receiver.complete(self.identifier, self.result)
        return []


def create_result_command(identifier_type: type, result_type: type) -> type:
    return make_dataclass(
        'ResultCommand',
        (('identifier', identifier_type), ('result', result_type)),
        bases=(BaseResultCommand,),
        frozen=True
    )


@dataclass(frozen=True)
class BaseRegisterCommand(DomainCommand):
    identifier: base.SubproblemId

    @classmethod
    def get_identifier(cls) -> str:
        return 'REGISTER'

    def invoke(self, receiver: base.SubproblemPool) -> List[Command]:
        if self.identifier in receiver.results:
            result = receiver.results[self.identifier]
            result_command = BaseResultCommand(self.identifier, result)
            return [result_command]

        if self.identifier in receiver.in_progress_pool:
            if self.identifier == receiver.get_id_in_progress_locally():
                if self._is_sender_priority_greater():
                    self._update_subproblem_owner(receiver)
                    return []
                else:
                    drop_command = BaseDropCommand(self.identifier)
                    return [drop_command]
            else:
                return []

        receiver.register(self.identifier, self.context.sender_address)
        return []

    def _update_subproblem_owner(self, pool: base.SubproblemPool):
        sender = self.context.sender_address
        pool.update_worker_address(self.identifier, sender)

    def _is_sender_priority_greater(self):
        sender_priority = self.context.sender_address.get_priority()
        receiver_priority = self.context.local_address.get_priority()
        return receiver_priority < sender_priority


def create_register_command(identifier_type: type) -> type:
    return make_dataclass(
        'RegisterCommand',
        (('identifier', identifier_type),),
        bases=(BaseRegisterCommand,),
        frozen=True
    )


@dataclass(frozen=True)
class BaseDropCommand(DomainCommand):
    identifier: base.SubproblemId

    @classmethod
    def get_identifier(cls) -> str:
        return 'DROP'

    def invoke(self, receiver: base.SubproblemPool) -> List[Command]:
        if self.identifier == receiver.get_id_in_progress_locally():
            sender = self.context.sender_address
            receiver.update_worker_address(self.identifier, sender)
        return []


def create_drop_command(identifier_type: type) -> type:
    return make_dataclass(
        'DropCommand',
        (('identifier', identifier_type),),
        bases=(BaseDropCommand,),
        frozen=True
    )


@dataclass(frozen=True)
class PruneCommand(DomainCommand):
    address: ConnectionSettings

    @classmethod
    def get_identifier(cls) -> str:
        return 'PRUNE'

    def invoke(self, receiver: base.SubproblemPool) -> List[Command]:
        ids = receiver.get_ids_in_progress_by_address(self.address)
        for identifier in ids:
            receiver.revert_in_progress(identifier)
        return []
