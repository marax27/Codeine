import json


def to_object(code: str):
    try:
        return json.loads(code)
    except json.JSONDecodeError as exc:
        raise DecodeError(exc)


class DecodeError(Exception):
    pass
