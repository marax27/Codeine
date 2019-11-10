from app.shared.networking import ConnectionSettings


def test_toTuple_sampleAddress_validTuple():
    given_address = '0.0.0.0'
    given_port = 12345
    expected_result = (given_address, given_port)

    sut = ConnectionSettings(given_address, given_port)
    actual_result = sut.to_tuple()

    assert actual_result == expected_result


def test_fromTuple_sampleAddress_validResult():
    given_address = '0.0.0.0'
    given_port = 12345
    given_tuple = (given_address, given_port)
    expected_result = ConnectionSettings(given_address, given_port)

    actual_result = ConnectionSettings.from_tuple(given_tuple)

    assert actual_result == expected_result
