from queue import Queue
from logging import Logger
from app.shared.networking import ConnectionSettings
from .message_broker import MessageBroker


class LoggingMessageBroker(MessageBroker):
    def __init__(self, connection_settings: ConnectionSettings, logger: Logger):
        super().__init__(connection_settings)
        self._logger = logger

    def run(self):
        self._logger.info('Starting.')
        try:
            super().run()
        except Exception as exc:
            self._logger.exception(f'An error has occurred: {exc}')
        self._logger.info('Exited gracefully.')
