import sys
import socket
from execute import execute_command, execute_process_with_pipes


RECEIVE_BUFFER_SIZE = 4096


def handle_tcp_connection(client_socket, execute_command_string, execute_process_path, upload_destination_path, download_source_path, enable_shell, enable_hex_dump):
    if upload_destination_path:
        _handle_file_upload(client_socket, upload_destination_path, enable_hex_dump)

    elif download_source_path:
        _handle_file_download(client_socket, download_source_path, enable_hex_dump)

    elif execute_process_path:
        execute_process_with_pipes(execute_process_path, client_socket)

    elif execute_command_string:
        _handle_execute_command(client_socket, execute_command_string, enable_hex_dump)

    elif enable_shell:
        _handle_interactive_shell(client_socket, enable_hex_dump)

    else:
        _handle_echo(client_socket, enable_hex_dump)

    client_socket.close()


def _handle_echo(client_socket, enable_hex_dump):
    from hex_dump import print_hex_dump
    try:
        while True:
            incoming_data = client_socket.recv(RECEIVE_BUFFER_SIZE)
            if not incoming_data:
                print("[*] Client disconnected.")
                break
            if enable_hex_dump:
                print_hex_dump(incoming_data, f"Received {len(incoming_data)} bytes from the socket")
            print(incoming_data.decode(errors="replace"), end="")
            sys.stdout.flush()
    except (ConnectionResetError, BrokenPipeError, OSError):
        print("[*] Client disconnected.")


def _handle_file_upload(client_socket, upload_destination_path, enable_hex_dump):
    from hex_dump import print_hex_dump
    received_file_bytes = b""

    try:
        while True:
            incoming_chunk = client_socket.recv(RECEIVE_BUFFER_SIZE)
            if not incoming_chunk:
                break
            received_file_bytes += incoming_chunk
    except (ConnectionResetError, BrokenPipeError, OSError):
        pass

    if enable_hex_dump:
        print_hex_dump(received_file_bytes, f"Received {len(received_file_bytes)} bytes from the socket")

    with open(upload_destination_path, "wb") as destination_file:
        destination_file.write(received_file_bytes)

    upload_result_message = f"[*] Saved {len(received_file_bytes)} bytes to {upload_destination_path}\n"
    print(upload_result_message, end="")


def _handle_file_download(client_socket, download_source_path, enable_hex_dump):
    from hex_dump import print_hex_dump

    try:
        with open(download_source_path, "rb") as source_file:
            file_bytes = source_file.read()
    except FileNotFoundError:
        error_message = f"[!] File not found: {download_source_path}\n"
        client_socket.send(error_message.encode())
        return

    if enable_hex_dump:
        print_hex_dump(file_bytes, f"Sent {len(file_bytes)} bytes to the socket")

    client_socket.sendall(file_bytes)
    client_socket.shutdown(socket.SHUT_WR)
    print(f"[*] Sent {len(file_bytes)} bytes from {download_source_path}")


def _handle_execute_command(client_socket, execute_command_string, enable_hex_dump):
    from hex_dump import print_hex_dump
    command_output = execute_command(execute_command_string)
    encoded_output = command_output.encode()
    if enable_hex_dump:
        print_hex_dump(encoded_output, f"Sent {len(encoded_output)} bytes to the socket")
    client_socket.send(encoded_output)


def _handle_interactive_shell(client_socket, enable_hex_dump):
    from hex_dump import print_hex_dump
    try:
        while True:
            shell_prompt = "<netkitten:#> "
            client_socket.send(shell_prompt.encode())

            received_command_data = ""

            while "\n" not in received_command_data:
                incoming_chunk = client_socket.recv(RECEIVE_BUFFER_SIZE)
                if not incoming_chunk:
                    print("[*] Client disconnected from shell.")
                    return
                received_command_data += incoming_chunk.decode(errors="replace")

            if enable_hex_dump:
                encoded_command = received_command_data.encode()
                print_hex_dump(encoded_command, f"Received {len(encoded_command)} bytes from the socket")

            shell_command_output = execute_command(received_command_data)
            encoded_output = shell_command_output.encode()

            if enable_hex_dump:
                print_hex_dump(encoded_output, f"Sent {len(encoded_output)} bytes to the socket")

            client_socket.send(encoded_output)

    except (ConnectionResetError, BrokenPipeError, OSError):
        print("[*] Client disconnected from shell.")


def handle_udp_connection(udp_server_socket, incoming_data, sender_address, execute_command_string, enable_shell, enable_hex_dump):
    from hex_dump import print_hex_dump

    if enable_hex_dump:
        print_hex_dump(incoming_data, f"Received {len(incoming_data)} bytes from the socket")

    if execute_command_string:
        command_output = execute_command(execute_command_string)
        encoded_output = command_output.encode()
        if enable_hex_dump:
            print_hex_dump(encoded_output, f"Sent {len(encoded_output)} bytes to the socket")
        udp_server_socket.sendto(encoded_output, sender_address)

    elif enable_shell:
        decoded_command = incoming_data.decode(errors="replace").strip()
        shell_output = execute_command(decoded_command)
        encoded_output = shell_output.encode()
        if enable_hex_dump:
            print_hex_dump(encoded_output, f"Sent {len(encoded_output)} bytes to the socket")
        udp_server_socket.sendto(encoded_output, sender_address)

    else:
        print(incoming_data.decode(errors="replace"), end="")
        sys.stdout.flush()