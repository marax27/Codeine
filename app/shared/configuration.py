from app.shared.files import get_project_file_path
import app.shared.json as json
from app.shared.dataclass import bind_dictionary_to


class Configuration:
    def __init__(self, package_name: str):
        self._package_name = package_name
        self._configuration = ConfigurationSection()

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
        return self._configuration.get(key)

    def _update(self, new_obj: dict):
        current, new = self._configuration, ConfigurationSection(new_obj)
        self._configuration = ConfigurationSection.combine(current, new)

    @staticmethod
    def _try_decode_json(code: str):
        try:
            return json.to_object(code)
        except json.DecodeError as exc:
            raise ConfigurationFormatError(exc)


class ConfigurationSection:
    def __init__(self, obj=None):
        self._configuration = obj if obj else {}

    def get(self, key: str):
        if key in self._configuration:
            value = self._configuration[key]
            if isinstance(value, dict):
                result = ConfigurationSection(value)
            elif isinstance(value, list):
                result = tuple(value)
            else:
                result = value
            return result
        raise KeyNotFoundError(key)

    def bind_as(self, bind_type: type):
        return bind_dictionary_to(bind_type, self._configuration)

    def keys(self) -> set:
        return set(self._configuration.keys())

    @staticmethod
    def combine(first, other):
        duplicate_keys = first.keys() & other.keys()
        if duplicate_keys:
            raise ConfigurationDuplicateKeysError(duplicate_keys)
        obj = first._configuration.copy()
        obj.update(other._configuration.copy())
        return ConfigurationSection(obj)


class ConfigurationError(Exception):
    pass


class ConfigurationFormatError(ConfigurationError):
    pass


class ConfigurationDuplicateKeysError(ConfigurationError):
    pass


class KeyNotFoundError(ConfigurationError):
    pass
