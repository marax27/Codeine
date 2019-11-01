
def bind_dictionary_to(dataclass: type, dictionary: dict):
    required_attributes = get_attributes(dataclass)
    provided_attributes = dictionary.keys()

    not_provided_attr = required_attributes.difference(provided_attributes)
    if not_provided_attr:
        raise BindingError(not_provided_attr)

    common_attributes = required_attributes.intersection(provided_attributes)
    binder = {key: dictionary[key] for key in common_attributes}
    return dataclass(**binder)


def get_attributes(dataclass) -> set:
    return set(dataclass.__dataclass_fields__.keys())


class BindingError(Exception):
    pass
