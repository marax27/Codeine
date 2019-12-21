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
        task_pool = challenge.create_task_pool()
        answer = challenge.create_state()
 
        while True:
            if task_pool.not_started_pool:
                subtask_id = task_pool.pop_identifier()
                task_pool.register(subtask_id)
                subtask = challenge.create_task(subtask_id, answer)
                subtask.run()
                subtask_result = subtask.result
                task_pool.complete(subtask_id, subtask_result)
            if subtask_result is not None:
                #placeholder for victory condition
                print (subtask_result.result)
                break
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
    logger.info('Gracefully stopped.')


def create_broker(connection_settings: ConnectionSettings) -> Broker:
    logger = get_logger('broker')
    connection = NetworkConnection(connection_settings)
    return LoggingBroker(connection, logger)


if __name__ == '__main__':
    initialize()
    main()
