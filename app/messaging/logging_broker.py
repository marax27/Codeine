from logging import Logger
from app.shared.networking import ConnectionSettings, NetworkIO
from .commands import Command
from .broker import Broker
from .commands import CommandMapper


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
            self._logger.exception(f'Packet -> Command mapping failed: {exc}')
            raise

    def _send(self, recipients, command):
        count = len(set(recipients))
        identifier = command.get_identifier()
        self._logger.info(f'Sending {identifier} to {count} recipients')
        command_as_bytes = self._command_mapper.map_to_bytes(command)
        self._logger.info(f'Sending command: {command_as_bytes.decode("utf-8")}')
        super()._send(recipients, command)
