import subprocess
import threading


def execute_command(command):
    command = command.strip()
    if not command:
        return ""
    try:
        command_output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        return command_output.decode()
    except subprocess.CalledProcessError as process_error:
        return process_error.output.decode()


def execute_process_with_pipes(process_path, client_socket):
    spawned_process = subprocess.Popen(
        process_path,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    receive_buffer_size = 4096

    def forward_process_output_to_socket():
        try:
            while True:
                output_data = spawned_process.stdout.read(receive_buffer_size)
                if not output_data:
                    break
                client_socket.send(output_data)
        except Exception:
            pass

    output_forwarding_thread = threading.Thread(target=forward_process_output_to_socket)
    output_forwarding_thread.daemon = True
    output_forwarding_thread.start()

    try:
        while True:
            incoming_data = client_socket.recv(receive_buffer_size)
            if not incoming_data:
                break
            spawned_process.stdin.write(incoming_data)
            spawned_process.stdin.flush()
    except Exception:
        pass
    finally:
        spawned_process.terminate()
        output_forwarding_thread.join(timeout=2)