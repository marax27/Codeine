import pytest

import app.shared.json as json
from app.messaging.topology import NetTopology
from app.messaging.messages import MessageMapper
from app.shared.networking import ConnectionSettings


def test_toObject_sampleObject_expectedDict():
    given_code = '{"a": 123, "b": "text"}'
    expected_result = {'a': 123, 'b': 'text'}

    actual_result = json.to_object(given_code)
    assert actual_result == expected_result


def test_toObject_invalidJSON_raiseDecodeError():
    given_code = '{"missing": "bracket"'

    with pytest.raises(json.DecodeError):
        json.to_object(given_code)


def test_topology_message_jsonMessage():
    network_connection_1 = ConnectionSettings("192.168.192.1", 2137)
    network_connection_2 = ConnectionSettings("192.168.192.2", 2137)
    agents = (network_connection_1, network_connection_2)
    message = NetTopology(agents)

    mapper = MessageMapper().register(NetTopology, "NETTOPO")
    message_as_bytes = mapper.map_to_bytes(message)
    message_from_bytes = mapper.map_from_bytes(message_as_bytes)

    assert message_from_bytes == message
