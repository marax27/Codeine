import pytest

import app.shared.json as json
from app.messaging.topology import NetTopology, ImAlive
from app.messaging.messages import MessageMapper
from app.shared.networking import ConnectionSettings


def test_topology_nettopology_jsonMessage():
    network_connection_1 = ConnectionSettings('192.168.192.1', 2137)
    network_connection_2 = ConnectionSettings('192.168.192.2', 2137)
    agents = (network_connection_1, network_connection_2)
    message = NetTopology(agents)

    mapper = MessageMapper().register(NetTopology, 'NETTOPO')
    message_as_bytes = mapper.map_to_bytes(message)
    message_from_bytes = mapper.map_from_bytes(message_as_bytes)

    assert message_from_bytes == message


def test_topology_imalive_jsonMessage():
    message = ImAlive()
    message_id = message.get_identifier()
    mapper = MessageMapper().register(ImAlive, message_id)

    message_as_bytes = mapper.map_to_bytes(message)
    message_from_bytes = mapper.map_from_bytes(message_as_bytes)

    assert message_from_bytes == message


def test_topology_imalive_containsId():
    message = ImAlive()
    message_id = message.get_identifier()
    mapper = MessageMapper().register(ImAlive, message_id)

    message_as_bytes = mapper.map_to_bytes(message)

    assert (message_id + '{}').encode('UTF-8') in message_as_bytes
