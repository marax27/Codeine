from time import sleep
from .shared.networking import ConnectionSettings
from .shared.configuration import Configuration
from .shared.logs import get_logger, initialize
from .messaging.message_broker import MessageBroker
from .messaging.logging_broker import LoggingMessageBroker


def main():
    config = Configuration(__package__) \
        .add_json_file('config.json')
    connection_settings = config.get('Connection').bind_as(ConnectionSettings)
    logger = get_logger(__package__)

    logger.info('Codeine started.')
    broker = create_broker(connection_settings)
    broker.start()

    try:
        while True:
            for message in broker.get_messages():
                logger.info(f'Received message: {message}')
            if not broker.is_alive():
                break
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    except BaseException as exc:
        logger.error(f'An unexpected exception has occurred: {exc}')

    logger.info('Gracefully stopping Codeine...')
    broker.stop()
    broker.join()
    logger.info('Gracefully stopped.')


def create_broker(connection_settings: ConnectionSettings) -> MessageBroker:
    logger = get_logger('message-broker')
    return LoggingMessageBroker(connection_settings, logger)


if __name__ == '__main__':
    initialize()
    main()
