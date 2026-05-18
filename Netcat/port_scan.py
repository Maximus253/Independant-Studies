import socket


CONNECTION_TIMEOUT_SECONDS = 1


def scan_single_port(target_host, target_port):
    scanner_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    scanner_socket.settimeout(CONNECTION_TIMEOUT_SECONDS)
    try:
        scanner_socket.connect((target_host, target_port))
        scanner_socket.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def scan_port_range(target_host, port_range_string):
    if "-" in port_range_string:
        range_parts = port_range_string.split("-")
        start_port = int(range_parts[0])
        end_port = int(range_parts[1])
        port_list = range(start_port, end_port + 1)
    else:
        port_list = [int(port_range_string)]

    open_ports_found = []

    for current_port in port_list:
        port_is_open = scan_single_port(target_host, current_port)
        if port_is_open:
            print(f"Connection to {target_host} port {current_port} [tcp] succeeded!")
            open_ports_found.append(current_port)
        else:
            if len(port_list) == 1:
                print(f"Connection to {target_host} port {current_port} [tcp] failed!")

    return open_ports_found