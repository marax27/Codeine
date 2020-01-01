from logging import Logger
from app.shared.networking import ConnectionSettings, NetworkIO
from .commands import Command
from .broker import Broker
from .commands import CommandMapper
from .topology import RecipientNotRegisteredError


class LoggingBroker(Broker):
    def __init__(self, connection: NetworkIO, logger: Logger, mapper: CommandMapper):
        super().__init__(connection, mapper)
        self._logger = logger

    def run(self):
        self._logger.info('Starting.')
        try:
            super().run()
        except Exception as exc:
            self._logger.exception(f'An error has occurred: {exc}')
        self._logger.info('Exited gracefully.')

    def _to_command(self, data: bytes) -> Command:
        try:
            return super()._to_command(data)
        except Exception as exc:
            self._logger.error(f'Packet -> Command mapping failed: {exc}')
            raise

    def _handle_single_outgoing(self, payload):
        try:
            super()._handle_single_outgoing(payload)
        except RecipientNotRegisteredError as exc:
            self._logger.warning(f'Cannot send a command to {payload.address}: {exc}')

    def _receive(self):
        result = super()._receive()
        if result is not None:
            self._logger.info(f'Received from {result.address}: {result.command}')
        return result

    def _send(self, recipients, command):
        identifier = command.get_identifier()
        command_as_bytes = self._command_mapper.map_to_bytes(command)
        self._logger.info(f'Sending {identifier} to {list(recipients)}: {command_as_bytes.decode("utf-8")}')
        super()._send(recipients, command)
