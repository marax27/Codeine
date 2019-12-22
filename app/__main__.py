from time import sleep
from .shared.networking import ConnectionSettings, NetworkConnection
from .shared.configuration import Configuration
from .shared.logs import get_logger, initialize
from .messaging.broker import Broker
from .messaging.logging_broker import LoggingBroker
from .computing import facade


def main():
    config = Configuration(__package__) \
        .add_json_file('config.json')
    connection_settings = config.get('Connection').bind_as(ConnectionSettings)
    logger = get_logger(__package__)

    logger.info('Codeine started.')
    broker = create_broker(connection_settings)
    broker.start()

    try:
        challenge = facade.get_computational_problem()
        subproblem_pool = challenge.create_subproblem_pool()
        state = challenge.create_state()

        subproblem_result = None
        subproblem_in_progress = False

        while True:
            if subproblem_result is not None:
                #placeholder for victory condition
                logger.info(subproblem_result.result)
                break
            if not subproblem_in_progress:
                if subproblem_pool.not_started_pool:
                    subproblem_id = subproblem_pool.pop_identifier()
                    subproblem_pool.register(subproblem_id)
                    subproblem = challenge.create_subproblem(subproblem_id, state)
                    subproblem.start()
                    subproblem_in_progress = True
                elif not subproblem_pool.not_started_pool:
                    #placeholder running out of subproblems
                    break
            if not subproblem.is_alive():
                subproblem_in_progress = False
                subproblem_result = subproblem.result
                subproblem_pool.complete(subproblem_id, subproblem_result)

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
    subproblem.stop()
    broker.join()
    subproblem.join()
    logger.info('Gracefully stopped.')


def create_broker(connection_settings: ConnectionSettings) -> Broker:
    logger = get_logger('broker')
    connection = NetworkConnection(connection_settings)
    return LoggingBroker(connection, logger)


if __name__ == '__main__':
    initialize()
    main()
