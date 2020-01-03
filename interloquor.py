import sys
from time import sleep
from app.shared.networking import NetworkConnection, ConnectionSettings, Packet


def main(args):
    try:
        connection, recipient = initialize(args[1:])
    except Exception as exc:
        print(f'Failed to process configuration: {exc}')
        print(f'Usage: {args[0]} port_number recipient_port_number')
        return

    netcon = NetworkConnection(connection)

    user_input = ''
    while user_input not in ('exit', 'quit', 'q'):
        show_received(netcon)
        sleep(0.1)
        show_received(netcon, '<!')

        inp = get_input()
        if inp == '':
            continue
        if inp != '.':
            user_input = inp
        data = user_input.encode('utf-8')
        netcon.send(Packet(data, recipient))

    packet = netcon.receive()
    print(packet)


def show_received(connection: NetworkConnection, prefix: str = '<:'):
    while True:
        received = connection.receive()
        if received is None:
            break
        print(f'{prefix} [{received.address}]\n\t{received.data}')


def get_input():
    print('?> ', end='')
    return input()


def initialize(args):
    connection = ConnectionSettings('0.0.0.0', int(args[0]))
    recipient = ConnectionSettings('0.0.0.0', int(args[1]))
    return connection, recipient


if __name__ == '__main__':
    main(sys.argv)