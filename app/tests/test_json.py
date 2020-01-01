import pytest

import app.shared.json as json


def test_toObject_sampleObject_expectedDict():
    given_code = '{"a": 123, "b": "text"}'
    expected_result = {'a': 123, 'b': 'text'}

    actual_result = json.to_object(given_code)
    assert actual_result == expected_result


def test_toObject_invalidJSON_raiseDecodeError():
    given_code = '{"missing": "bracket"'

    with pytest.raises(json.DecodeError):
        json.to_object(given_code)
