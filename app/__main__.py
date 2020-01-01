from time import sleep
from typing import Iterable, Optional
from .shared.networking import ConnectionSettings, NetworkConnection
from .shared.configuration import Configuration
from .shared.logs import get_logger, initialize
from .messaging.broker import Broker
from .messaging.logging_broker import LoggingBroker
from .computing.facade import get_computational_problem
from .computing.base import Subproblem, SubproblemResult, SubproblemPool
from .computing.domain_commands import DomainCommand
from .app import ApplicationSettings, ComputationManager, EmptySubproblemPoolError
from .messaging.commands import CommandMapper
from .messaging.command_handler import CommandHandler, CommandNotRegisteredException


ResultCommand: type = None
RegisterCommand: type = None


def main(computation_manager: ComputationManager):

    config = Configuration(__package__) \
        .add_json_file('config.json')
    connection_settings = config.get('Connection').bind_as(ConnectionSettings)
    app_settings = config.get('Application').bind_as(ApplicationSettings)
    logger = get_logger(__package__)

    mode_name = 'active' if app_settings.active_mode else 'passive'
    logger.info(f'Codeine started in {mode_name} mode.')

    handler = create_command_handler(computation_manager.pool)
    broker = create_broker(connection_settings, create_command_mapper())
    broker.start()
    broker.discover_network()
    subproblem: Optional[Subproblem] = None
    active_mode = app_settings.active_mode

    try:
        while True:
            if active_mode:
                if subproblem is None:
                    try:
                        subproblem = computation_manager.create_random()
                        subproblem.start()
                        identifier = subproblem.identifier
                        broker.broadcast(RegisterCommand(identifier))
                        logger.info(f'Subproblem #{identifier} has started.')
                    except EmptySubproblemPoolError:
                        logger.warning('No more subproblems to take.')
                        active_mode = False
                elif not subproblem.is_alive():
                    identifier = subproblem.identifier
                    result = subproblem.result
                    computation_manager.handle_completed(subproblem)
                    broadcast_result(subproblem, broker)
                    subproblem = None
                    logger.info(f'Subproblem #{identifier} has ended (result: {result}).')

                results = computation_manager.pool.results
                if is_stop_condition_met(results.values()):
                    active_mode = False
                    logger.info(f'Stop condition is met: {results}')
                elif computation_manager.all_subproblems_finished():
                    active_mode = False
                    logger.info(f'All subproblems finished: {results}')

            for payload in broker.get_payloads():
                try:
                    logger.info(f'Received command from {payload.address}: {payload.command}')
                    responses = handler.handle(payload)
                    for response in responses:
                        broker.send(response)
                except CommandNotRegisteredException as exc:
                    logger.error(f'Unregistered command received from {payload.address}: {exc}')

                logger.info(computation_manager.pool.results)
            if not broker.is_alive():
                break
            sleep(0.01)
    except KeyboardInterrupt:
        pass
    except BaseException as exc:
        logger.exception(f'An unexpected exception has occurred: {exc}')

    logger.info('Gracefully stopping Codeine...')
    broker.stop()
    broker.join()

    if subproblem:
        subproblem.stop()
        subproblem.join()

    logger.info('Gracefully stopped.')


def is_stop_condition_met(results: Iterable[SubproblemResult]) -> bool:
    return any(r.result is not None for r in results)


def create_broker(connection_settings: ConnectionSettings, mapper: CommandMapper) -> Broker:
    logger = get_logger('broker')
    connection = NetworkConnection(connection_settings)
    return LoggingBroker(connection, logger, mapper)


def create_command_mapper() -> CommandMapper:
    return CommandMapper() \
        .register(ResultCommand) \
        .register(RegisterCommand) \
        .register(DropCommand)


def create_command_handler(pool: SubproblemPool) -> CommandHandler:
    return CommandHandler() \
        .register(DomainCommand, pool)


def broadcast_result(subproblem: Subproblem, broker: Broker):
    command = ResultCommand(subproblem.identifier, subproblem.result)
    broker.broadcast(command)


if __name__ == '__main__':
    initialize()
    PROBLEM = get_computational_problem()
    ResultCommand = PROBLEM.result_command_type
    RegisterCommand = PROBLEM.register_command_type
    DropCommand = PROBLEM.drop_command_type
    main(ComputationManager(PROBLEM))
