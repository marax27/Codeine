import pytest
from app.shared.networking import ConnectionSettings, Packet


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


def test_packet_sampleData_expectedPacket():
    given_data = b'12345678'
    given_address = ConnectionSettings('0.0.0.0', 12345)

    actual_packet = Packet(given_data, given_address)

    assert actual_packet.address == given_address
    assert actual_packet.data == given_data


@pytest.mark.parametrize('first,other', [
    (ConnectionSettings('1.2.3.4', 101), ConnectionSettings('1.2.3.4', 100)),
    (ConnectionSettings('1.2.3.5', 100), ConnectionSettings('1.2.3.4', 100)),
    (ConnectionSettings('2.1.1.1', 100), ConnectionSettings('1.1.1.2', 100)),
])
def test_getPriority_sampleAddresses_firstGreaterThanOther(
        first: ConnectionSettings,
        other: ConnectionSettings):

    assert first.get_priority() > other.get_priority()
