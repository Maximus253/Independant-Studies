import socket


CONNECTION_BACKLOG_LIMIT = 5
ACCEPT_TIMEOUT_SECONDS = 1


def start_tcp_listener(listening_host, listening_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.settimeout(ACCEPT_TIMEOUT_SECONDS)
    server_socket.bind((listening_host, listening_port))
    server_socket.listen(CONNECTION_BACKLOG_LIMIT)

    print(f"[*] Listening on {listening_host}:{listening_port}")

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            print(f"[*] Accepted connection from {client_address[0]}:{client_address[1]}")
            return client_socket
        except socket.timeout:
            continue


def start_udp_listener(listening_host, listening_port):
    udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_server_socket.settimeout(ACCEPT_TIMEOUT_SECONDS)
    udp_server_socket.bind((listening_host, listening_port))

    print(f"[*] UDP listening on {listening_host}:{listening_port}")

    while True:
        try:
            incoming_data, sender_address = udp_server_socket.recvfrom(65535)
            print(f"[*] Received UDP packet from {sender_address[0]}:{sender_address[1]}")
            return udp_server_socket, incoming_data, sender_address
        except socket.timeout:
            continue