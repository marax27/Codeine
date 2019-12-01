from logging import Logger
from app.shared.networking import ConnectionSettings
from .messages import Message
from .message_broker import MessageBroker
from .topology import NetTopologyMessage


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

    def _to_message(self, data: bytes) -> Message:
        try:
            return super()._to_message(data)
        except Exception as exc:
            self._logger.exception(f'Packet -> Message mapping failed: {exc}')
            raise

    def _handle_imalive(self, address: ConnectionSettings):
        self._logger.info(f'IMALIVE notification from {address}')
        super()._handle_imalive(address)
        self._logger.info(f'Agents: {self._agents}')

    def _handle_nettopo(self, message, sender_address):
        self._logger.info(f'Network topology update: {message.agents}')
        super()._handle_nettopo(message, sender_address)
        self._logger.info(f'Agents: {self._agents}')
