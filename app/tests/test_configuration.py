import pytest

import app.shared.configuration as cfg


def test_addJsonCodeAndGet_stringEntry_entryPresentInConfiguration():
    given_code = '{ "SampleKey": "SampleValue" }'
    sut = cfg.Configuration(None).add_json_code(given_code)
    assert sut.get('SampleKey') == 'SampleValue'


def test_addJsonCodeAndGet_integerEntry_entryPresentInConfiguration():
    given_code = '{ "SampleKey": 12345 }'
    sut = cfg.Configuration(None).add_json_code(given_code)
    assert sut.get('SampleKey') == 12345


def test_addJsonCodeAndGet_floatEntry_entryPresentInConfiguration():
    given_code = '{ "SampleKey": 3.14159 }'
    sut = cfg.Configuration(None).add_json_code(given_code)
    assert sut.get('SampleKey') == 3.14159


def test_addJsonCodeAndGet_nullEntry_entryPresentInConfiguration():
    given_code = '{ "SampleKey": null }'
    sut = cfg.Configuration(None).add_json_code(given_code)
    assert sut.get('SampleKey') is None


def test_get_nonexistentKey_raiseError():
    sut = cfg.Configuration(None)
    with pytest.raises(cfg.KeyNotFoundError):
        sut.get('SampleKey')


def test_addJsonCode_twoConfigsWithCommonKeys_raiseError():
    given_first_code = '{ "a": 123, "b": 999 }'
    given_other_code = '{ "b": "abc", "x": 0 }'

    sut = cfg.Configuration(None).add_json_code(given_first_code)
    with pytest.raises(cfg.ConfigurationDuplicateKeysError):
        sut.add_json_code(given_other_code)
