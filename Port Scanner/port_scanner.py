from concurrent.futures import ThreadPoolExecutor
import socket
import time

def divide_port_range(port_range, max_workers): 
    port_ranges = port_range.split('-')
    port_chunks = []

    chunk_size = int((int(port_ranges[1]) - int(port_ranges[0])) / max_workers)

    for x in range(max_workers):
        start = int(port_ranges[0]) + (chunk_size * x)
        end = start + chunk_size
        port_chunks.append([start, end])
    return port_chunks

def scan_tcp(ip_address, port_chunk):
    print(f"[~] Scanning {ip_address} from {port_chunk[0]} to {port_chunk[1]} with TCP IPV4")
    for port in range(int(port_chunk[0]), int(port_chunk[1])):
        try:
            scan_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            scan_socket.settimeout(2)
            scan_socket.connect((ip_address, port))
            print(f" Port {port} is open!")
        except: None
        finally:
            scan_socket.close()

print(f'Please enter ip address: ')
ip_address = input()
print(f'Please enter number of threads: ')
max_workers = int(input())
port_range = '0-10000'

port_chunks = divide_port_range(port_range, max_workers)

start_time = time.time()

with ThreadPoolExecutor(max_workers = max_workers) as executor:
    executor.map(scan_tcp, [ip_address] * len(port_chunks), port_chunks)

end_time = time.time()

print(f'Scanned {port_range} ports in {end_time - start_time} seconds.')