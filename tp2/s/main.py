import socket
import threading
import struct
import sys

window_size = 10
base = 0
next_packet = 0

base_lock = threading.Lock()
next_packet_lock = threading.Lock()

def calculate_checksum(payload):
    s = 0
    for i in range(len(payload)):
        s <<= 8
        s += payload[i]
        s = (s & 0xffff) + (s >> 16)
    return ~s & 0xffff

def create_packet(seq_n, ack_n, payload="".encode()):
    checksum = calculate_checksum(payload)
    length = 8 + len(payload)
    return struct.pack("!HHHH", checksum, length, seq_n, ack_n) + payload

def divide_into_byte_chunks(file_name, payload_size):
    f = open(file_name, "r")
    content = f.read()
    f.close()
    n = int(len(content)/payload_size) + 1
    byte_chunks = []
    for i in range(1, n):
        byte_chunks.append(content[(i - 1)*payload_size:i*payload_size].encode())
    return byte_chunks

def file_sender(src_ip, src_port, dst_ip, dst_port, file_name):
    global window_size, base, next_packet
    byte_chunks = divide_into_byte_chunks(file_name, 512)
    file_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack_receiver_socket.bind((src_ip, src_port))
    ack_receiver_socket.settimeout(1)
    next_packet_lock.acquire()
    while next_packet < len(byte_chunks):
        next_packet_lock.release()
        next_packet_lock.acquire()
        base_lock.acquire()
        if next_packet < base + window_size:
            file_sender_socket.sendto(create_packet(next_packet + 1, 0, byte_chunks[next_packet]), (dst_ip, dst_port))
            next_packet += 1
            threading.Thread(target=ack_receiver, args=(ack_receiver_socket,)).start()
        base_lock.release()
        next_packet_lock.release()
        next_packet_lock.acquire()
    next_packet_lock.release()

def ack_receiver(ack_receiver_socket):
    global base, next_packet
    try:
        packet, _ = ack_receiver_socket.recvfrom(1024)
        checksum, length, seq_n, ack_n = struct.unpack("!HHHH", packet[:8])
        base_lock.acquire()
        if ack_n > base:
            base = ack_n
        base_lock.release()
    except socket.timeout:
        next_packet_lock.acquire()
        next_packet = base
        next_packet_lock.release()

def main():
    t_client = threading.Thread(target=file_sender, args=("10.10.3.1", 8080, "10.10.3.2", 8080, sys.argv[1]))
    t_client.start()
    t_client.join()

main()
