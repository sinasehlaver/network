import socket
import threading
import struct
import sys

def calculate_checksum(payload):
    s = 0
    for i in range(len(payload)):
        s <<= 8
        s += payload[i]
        s = (s & 0xffff) + (s >> 16)
    return ~s & 0xffff

def create_packet(seq_n, ack_n, payload):
    checksum = calculate_checksum(payload)
    length = 8 + len(payload)
    return struct.pack("!HHHH", checksum, length, seq_n, ack_n) + payload

def divide_into_chunks(file_name, payload_size):
    f = open(file_name, "rb")
    content = f.read()
    f.close()
    n = int(len(content)/payload_size) + 1
    chunks = []
    for i in range(1, n):
        chunks.append(content[(i - 1)*payload_size:i*payload_size])
    return chunks

def client(src_ip, src_port, dst_ip, dst_port, file_name):
    chunks = divide_into_chunks(file_name, 512)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind((src_ip, src_port))
    for i in range(len(chunks)):
        client_socket.sendto(create_packet(i, 1, chunks[i]), (dst_ip, dst_port))

def main():
    t_client = threading.Thread(target=client, args=("10.10.3.1", 8080, "10.10.3.2", 8080, sys.argv[1]))
    t_client.start()
    t_client.join()

main()
