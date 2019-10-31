import os


def get_project_file_path(package_name, filename):
    return os.path.join(os.getcwd(), *package_name.split('.'), filename)
