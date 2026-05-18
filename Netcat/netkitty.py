import argparse
import sys
import threading
from send import send_tcp_data, send_udp_data, receive_tcp_file
from listen import start_tcp_listener, start_udp_listener
from handle import handle_tcp_connection, handle_udp_connection
from port_scan import scan_port_range


def parse_command_line_arguments():
    argument_parser = argparse.ArgumentParser(
        description="netkitten - A Python netcat replacement",
        usage="%(prog)s [options] [target] [port]",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Listen for TCP on port 4444:
    python netkitty.py -l -p 4444

  Connect to a TCP host:
    python netkitty.py -t 127.0.0.1 -p 4444

  Listen for UDP on port 4444:
    python netkitty.py -l -p 4444 -u

  Connect via UDP:
    python netkitty.py -t 127.0.0.1 -p 4444 -u

  Scan a single port:
    python netkitty.py -z 127.0.0.1 8888

  Scan a port range:
    python netkitty.py -z 127.0.0.1 8880-8890

  Listen and spawn a shell:
    python netkitty.py -l -p 4444 -s

  Listen and execute a process (reverse shell):
    python netkitty.py -l -p 4444 -e cmd.exe

  Listen and run one command on connect:
    python netkitty.py -l -p 4444 -c "whoami"

  Listen and receive an uploaded file:
    python netkitty.py -l -p 4444 -U received.txt

  Send a file (upload):
    python netkitty.py -t 127.0.0.1 -p 4444 -f testfile.txt

  Listen and serve a file for download:
    python netkitty.py -l -p 4444 -D sendthisfile.txt

  Connect and save a downloaded file:
    python netkitty.py -t 127.0.0.1 -p 4444 -R savedfile.txt

  Listen with hex dump:
    python netkitty.py -l -p 4444 -x

  Connect with hex dump:
    python netkitty.py -t 127.0.0.1 -p 4444 -x
        """
    )

    argument_parser.add_argument(
        "-t", "--target",
        default="0.0.0.0",
        help="Target host IP address"
    )

    argument_parser.add_argument(
        "-p", "--port",
        type=int,
        default=None,
        help="Port number to connect to or listen on"
    )

    argument_parser.add_argument(
        "-l", "--listen",
        action="store_true",
        help="Listen mode: wait for an incoming connection"
    )

    argument_parser.add_argument(
        "-u", "--udp",
        action="store_true",
        help="Use UDP instead of TCP"
    )

    argument_parser.add_argument(
        "-z", "--zero-io",
        nargs=2,
        metavar=("HOST", "PORT_OR_RANGE"),
        help="Port scan mode: test if port(s) are open without sending data"
    )

    argument_parser.add_argument(
        "-e", "--execute",
        default="",
        help="Execute this process and pipe its I/O to the connection (e.g. cmd.exe)"
    )

    argument_parser.add_argument(
        "-c", "--command",
        default="",
        help="Run this single command on connect and return the output"
    )

    argument_parser.add_argument(
        "-U", "--upload",
        default="",
        help="Receive an uploaded file and save it to this path (listener mode)"
    )

    argument_parser.add_argument(
        "-D", "--download-serve",
        default="",
        help="Serve this file to whoever connects (listener mode)"
    )

    argument_parser.add_argument(
        "-R", "--receive-file",
        default="",
        help="Connect and save the incoming file to this path (client mode)"
    )

    argument_parser.add_argument(
        "-s", "--shell",
        action="store_true",
        help="Spawn an interactive command shell over the connection"
    )

    argument_parser.add_argument(
        "-f", "--file",
        default="",
        help="Send this file on connect (upload)"
    )

    argument_parser.add_argument(
        "-x", "--hex-dump",
        action="store_true",
        help="Print a hex dump of all transmitted and received data"
    )

    return argument_parser.parse_args()


def read_file_as_bytes(file_path):
    with open(file_path, "rb") as input_file:
        return input_file.read()


def run_tcp_listener(target_host, target_port, execute_command_string, execute_process_path, upload_destination_path, download_source_path, enable_shell, enable_hex_dump):
    try:
        while True:
            client_socket = start_tcp_listener(target_host, target_port)

            connection_thread = threading.Thread(
                target=handle_tcp_connection,
                args=(client_socket, execute_command_string, execute_process_path, upload_destination_path, download_source_path, enable_shell, enable_hex_dump)
            )
            connection_thread.daemon = True
            connection_thread.start()

    except KeyboardInterrupt:
        print("\n[*] TCP listener stopped by user.")
        sys.exit(0)


def run_udp_listener(target_host, target_port, execute_command_string, enable_shell, enable_hex_dump):
    try:
        while True:
            udp_server_socket, incoming_data, sender_address = start_udp_listener(target_host, target_port)
            handle_udp_connection(udp_server_socket, incoming_data, sender_address, execute_command_string, enable_shell, enable_hex_dump)

    except KeyboardInterrupt:
        print("\n[*] UDP listener stopped by user.")
        sys.exit(0)


def main():
    parsed_arguments = parse_command_line_arguments()

    target_host = parsed_arguments.target
    target_port = parsed_arguments.port
    listen_mode_enabled = parsed_arguments.listen
    use_udp_protocol = parsed_arguments.udp
    zero_io_scan_args = parsed_arguments.zero_io
    execute_process_path = parsed_arguments.execute
    execute_command_string = parsed_arguments.command
    upload_destination_path = parsed_arguments.upload
    download_source_path = parsed_arguments.download_serve
    receive_file_save_path = parsed_arguments.receive_file
    enable_shell = parsed_arguments.shell
    file_path_to_send = parsed_arguments.file
    enable_hex_dump = parsed_arguments.hex_dump

    if zero_io_scan_args:
        scan_host = zero_io_scan_args[0]
        scan_port_or_range = zero_io_scan_args[1]
        scan_port_range(scan_host, scan_port_or_range)
        return

    if listen_mode_enabled:
        if target_port is None:
            print("[!] Listening requires a port. Use -p to specify one.")
            sys.exit(1)
        if use_udp_protocol:
            run_udp_listener(target_host, target_port, execute_command_string, enable_shell, enable_hex_dump)
        else:
            run_tcp_listener(target_host, target_port, execute_command_string, execute_process_path, upload_destination_path, download_source_path, enable_shell, enable_hex_dump)
    else:
        if target_port is None:
            print("[!] Connecting requires a port. Use -p to specify one.")
            sys.exit(1)

        if receive_file_save_path:
            receive_tcp_file(target_host, target_port, receive_file_save_path, enable_hex_dump)
            return

        if file_path_to_send:
            initial_buffer_bytes = read_file_as_bytes(file_path_to_send)
        elif not sys.stdin.isatty():
            initial_buffer_bytes = sys.stdin.buffer.read()
        else:
            initial_buffer_bytes = b""

        if use_udp_protocol:
            send_udp_data(target_host, target_port, initial_buffer_bytes, enable_hex_dump)
        else:
            send_tcp_data(target_host, target_port, initial_buffer_bytes, enable_hex_dump)


if __name__ == "__main__":
    main()