from .shared.configuration import Configuration
from .shared.logs import get_logger, initialize
from .computing.facade import get_computational_problem


logger = get_logger(__package__)


def main():
    config = Configuration(__package__) \
        .add_json_file('config.json')

    computation_problem = get_computational_problem()

    logger.info(f'Project Codeine started with configuration: {config}')
    logger.info(f'Computational problem: {computation_problem}')


if __name__ == '__main__':
    initialize()
    main()
