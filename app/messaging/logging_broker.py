from logging import Logger
from app.shared.networking import ConnectionSettings, NetworkConnection
from .commands import Command
from .broker import Broker


class LoggingBroker(Broker):
    def __init__(self, connection: NetworkConnection, logger: Logger):
        super().__init__(connection)
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
        super()._send(recipients, command)
