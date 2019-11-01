import pytest

import app.shared.configuration as cfg


@pytest.mark.parametrize('given_json_value, expected_value', [
        ('"SampleValue"', 'SampleValue'), ('123', 123), ('3.14', 3.14)
    ])
def test_addJsonCodeAndGet_sampleEntry_entryPresentInConfiguration(given_json_value, expected_value):
    given_code = f'{{ "SampleKey": {given_json_value} }}'
    sut = cfg.Configuration(None).add_json_code(given_code)
    assert sut.get('SampleKey') == expected_value


def test_addJsonCodeAndGet_nullEntry_entryPresentInConfiguration():
    given_code = '{ "SampleKey": null }'
    sut = cfg.Configuration(None).add_json_code(given_code)
    assert sut.get('SampleKey') is None


def test_addJsonCodeAndGet_dictionaryEntry_resultContainsExpectedEntry():
    given_code = '{ "SampleKey": { "A": 123 } }'
    sut = cfg.Configuration(None).add_json_code(given_code)
    section = sut.get('SampleKey')
    assert section.get('A') == 123


def test_get_nonexistentKey_raiseError():
    given_code = '{ "SampleKey": 123 }'
    sut = cfg.Configuration(None).add_json_code(given_code)
    with pytest.raises(cfg.KeyNotFoundError):
        sut.get('NonexistentKey')


def test_addJsonCode_twoConfigsWithCommonKeys_raiseError():
    given_first_code = '{ "a": 123, "b": 999 }'
    given_other_code = '{ "b": "abc", "x": 0 }'

    sut = cfg.Configuration(None).add_json_code(given_first_code)
    with pytest.raises(cfg.ConfigurationDuplicateKeysError):
        sut.add_json_code(given_other_code)
