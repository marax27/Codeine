from time import sleep
from typing import Optional
from .shared.networking import ConnectionSettings, NetworkConnection
from .shared.configuration import Configuration
from .shared.logs import get_logger, initialize
from .messaging.broker import Broker
from .messaging.logging_broker import LoggingBroker
from .computing import facade
from .computing.base import Subproblem
from .app import ApplicationSettings


def main():
    config = Configuration(__package__) \
        .add_json_file('config.json')
    connection_settings = config.get('Connection').bind_as(ConnectionSettings)
    app_settings = config.get('Application').bind_as(ApplicationSettings)
    logger = get_logger(__package__)

    mode_name = 'active' if app_settings.active_mode else 'passive'
    logger.info(f'Codeine started in {mode_name} mode.')

    broker = create_broker(connection_settings)
    broker.start()
    subproblem: Optional[Subproblem] = None
    active_mode = app_settings.active_mode

    try:
        challenge = facade.get_computational_problem()
        subproblem_pool = challenge.create_subproblem_pool()
        state = challenge.create_state()

        while True:
            if active_mode:
                if subproblem is None:
                    identifier = subproblem_pool.pop_identifier()
                    subproblem_pool.register(identifier)
                    subproblem = challenge.create_subproblem(identifier, state)
                    subproblem.start()
                    logger.info(f'Subproblem #{identifier} has started.')
                elif not subproblem.is_alive():
                    identifier = subproblem.identifier
                    result = subproblem.result
                    subproblem = None
                    subproblem_pool.complete(identifier, result)
                    logger.info(f'Subproblem #{identifier} has ended.')

                    if result is not None:
                        logger.info(f'Solution found: {result}.')
                        active_mode = False

            for command in broker.get_commands():
                logger.info(f'Received command: {command}')
            if not broker.is_alive():
                break
            sleep(0.01)
    except KeyboardInterrupt:
        pass
    except BaseException as exc:
        logger.error(f'An unexpected exception has occurred: {exc}')

    logger.info('Gracefully stopping Codeine...')
    broker.stop()
    broker.join()

    if subproblem:
        subproblem.stop()
        subproblem.join()

    logger.info('Gracefully stopped.')


def create_broker(connection_settings: ConnectionSettings) -> Broker:
    logger = get_logger('broker')
    connection = NetworkConnection(connection_settings)
    return LoggingBroker(connection, logger)


if __name__ == '__main__':
    initialize()
    main()
