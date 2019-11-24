from .shared.configuration import Configuration


def main():
    config = Configuration(__package__) \
        .add_json_file('config.json')

    print(f'Project Codeine started with configuration: {config}')


if __name__ == "__main__":
    main()
