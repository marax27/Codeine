from .shared.configuration import Configuration
from .computing.facade import TaskFactory, TaskPool


def main():
    config = Configuration(__package__) \
        .add_json_file('config.json')

    print(f'Project Codeine started with configuration: {config}')

    task_pool = TaskPool()
    task_factory = TaskFactory()


if __name__ == "__main__":
    main()
