from .shared.configuration import Configuration
from .computing.facade import get_computational_problem


def main():
    config = Configuration(__package__) \
        .add_json_file('config.json')

    computation_problem = get_computational_problem()

    print(f'Project Codeine started with configuration: {config}')
    print(f'Computational problem: {computation_problem}')


if __name__ == "__main__":
    main()
