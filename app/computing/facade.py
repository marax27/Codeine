from app.shared.configuration import Configuration
from .base import ComputationalProblem


def get_computational_problem() -> ComputationalProblem:
    configuration = Configuration(__package__) \
        .add_json_file('config.json')

    path = 'app.computing.' + configuration.get('problemModule')
    problem_module = __import__(path, fromlist=[None])

    return problem_module.ComputationalProblem()
