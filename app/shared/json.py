import json


def to_object(code: str):
    try:
        return json.loads(code)
    except json.JSONDecodeError as exc:
        raise DecodeError(exc)


def from_object(obj) -> str:
    return json.dumps(obj)


class DecodeError(Exception):
    pass
