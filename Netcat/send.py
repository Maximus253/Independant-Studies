import socket
import sys


RECEIVE_BUFFER_SIZE = 4096


def send_tcp_data(target_host, target_port, initial_buffer_bytes, enable_hex_dump):
    from hex_dump import print_hex_dump

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((target_host, target_port))
    except ConnectionRefusedError:
        print(f"[!] Connection to {target_host}:{target_port} refused.")
        return

    if initial_buffer_bytes:
        if enable_hex_dump:
            print_hex_dump(initial_buffer_bytes, f"Sent {len(initial_buffer_bytes)} bytes to the socket")
        client_socket.sendall(initial_buffer_bytes)
        client_socket.shutdown(socket.SHUT_WR)

        try:
            server_response = b""
            while True:
                incoming_chunk = client_socket.recv(RECEIVE_BUFFER_SIZE)
                if not incoming_chunk:
                    break
                server_response += incoming_chunk
            if server_response:
                if enable_hex_dump:
                    print_hex_dump(server_response, f"Received {len(server_response)} bytes from the socket")
                print(server_response.decode(errors="replace"), end="")
        except (ConnectionResetError, BrokenPipeError, OSError):
            pass
        finally:
            client_socket.close()
        return

    try:
        while True:
            user_input = input("")
            user_input += "\n"
            encoded_input = user_input.encode()

            if enable_hex_dump:
                print_hex_dump(encoded_input, f"Sent {len(encoded_input)} bytes to the socket")

            client_socket.send(encoded_input)

            received_response = b""

            while True:
                incoming_chunk = client_socket.recv(RECEIVE_BUFFER_SIZE)
                if not incoming_chunk:
                    break
                received_response += incoming_chunk
                if len(incoming_chunk) < RECEIVE_BUFFER_SIZE:
                    break

            if received_response:
                if enable_hex_dump:
                    print_hex_dump(received_response, f"Received {len(received_response)} bytes from the socket")
                print(received_response.decode(errors="replace"), end="")

    except KeyboardInterrupt:
        print("\n[*] Connection closed by user.")
    except (ConnectionResetError, BrokenPipeError, OSError):
        print("\n[*] Connection lost.")
    finally:
        client_socket.close()


def receive_tcp_file(target_host, target_port, save_file_path, enable_hex_dump):
    from hex_dump import print_hex_dump

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((target_host, target_port))
    except ConnectionRefusedError:
        print(f"[!] Connection to {target_host}:{target_port} refused.")
        return

    print(f"[*] Connected. Receiving file and saving to {save_file_path}")

    received_file_bytes = b""

    try:
        while True:
            incoming_chunk = client_socket.recv(RECEIVE_BUFFER_SIZE)
            if not incoming_chunk:
                break
            received_file_bytes += incoming_chunk
    except (ConnectionResetError, BrokenPipeError, OSError):
        pass
    finally:
        client_socket.close()

    if enable_hex_dump:
        print_hex_dump(received_file_bytes, f"Received {len(received_file_bytes)} bytes from the socket")

    with open(save_file_path, "wb") as output_file:
        output_file.write(received_file_bytes)

    print(f"[*] Saved {len(received_file_bytes)} bytes to {save_file_path}")


def send_udp_data(target_host, target_port, initial_buffer_bytes, enable_hex_dump):
    from hex_dump import print_hex_dump

    udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_client_socket.settimeout(5)

    target_address = (target_host, target_port)

    if initial_buffer_bytes:
        if enable_hex_dump:
            print_hex_dump(initial_buffer_bytes, f"Sent {len(initial_buffer_bytes)} bytes to the socket")
        udp_client_socket.sendto(initial_buffer_bytes, target_address)

    try:
        while True:
            if not initial_buffer_bytes:
                user_input = input("")
                user_input += "\n"
                encoded_input = user_input.encode()
                if enable_hex_dump:
                    print_hex_dump(encoded_input, f"Sent {len(encoded_input)} bytes to the socket")
                udp_client_socket.sendto(encoded_input, target_address)

            try:
                response_data, server_address = udp_client_socket.recvfrom(RECEIVE_BUFFER_SIZE)
                if enable_hex_dump:
                    print_hex_dump(response_data, f"Received {len(response_data)} bytes from the socket")
                print(response_data.decode(errors="replace"), end="")
            except socket.timeout:
                print("[*] No response received (timeout).")

            initial_buffer_bytes = b""

    except KeyboardInterrupt:
        print("\n[*] UDP session closed by user.")
    finally:
        udp_client_socket.close()