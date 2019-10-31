from app.shared.files import get_project_file_path
import app.shared.json as json


class Configuration:
    def __init__(self, package_name: str):
        self._package_name = package_name
        self._configuration = dict()

    def add_json_file(self, filename: str):
        path = get_project_file_path(self._package_name, filename)
        file_content = open(path, 'r').read()
        self.add_json_code(file_content)
        return self

    def add_json_code(self, code: str):
        obj = Configuration._try_decode_json(code)
        self._update(obj)
        return self

    def get(self, key: str):
        if key in self._configuration:
            return self._configuration[key]
        raise KeyNotFoundError(key)

    def _update(self, new_configuration: dict):
        duplicate_keys = self._configuration.keys() & new_configuration.keys()
        if duplicate_keys:
            raise ConfigurationDuplicateKeysError(duplicate_keys)
        self._configuration.update(new_configuration)

    @staticmethod
    def _try_decode_json(code: str):
        try:
            return json.to_object(code)
        except json.DecodeError as exc:
            raise ConfigurationFormatError(exc)


class ConfigurationError(Exception):
    pass


class ConfigurationFormatError(ConfigurationError):
    pass


class ConfigurationDuplicateKeysError(ConfigurationError):
    pass


class KeyNotFoundError(ConfigurationError):
    pass
