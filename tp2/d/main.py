import socket
import threading
import struct
import sys

payload_size = 512
N = 5*1024*1024//payload_size

byte_chunks = [None] * N

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

def file_receiver(src_ip, src_port, dst_ip, dst_port, file_name):
    global byte_chunks
    last_ack_packet = create_packet(0, 0)
    file_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    file_receiver_socket.bind((src_ip, src_port))
    ack_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        packet, _ = file_receiver_socket.recvfrom(1024)
        (checksum, length, seq_n, ack_n), payload = struct.unpack("!HHHH", packet[:8]), packet[8:]
        if seq_n == 0 and ack_n == 0:
            break
        if checksum == calculate_checksum(payload):
            if byte_chunks[seq_n - 1] == None:
                byte_chunks[seq_n - 1] = payload
            ack_sender_socket.sendto(create_packet(0, seq_n), (dst_ip, dst_port))
    f = open(file_name, "wb+")
    f.writelines(byte_chunks)
    f.close()

def main():
    t_server = threading.Thread(target=file_receiver, args=("10.10.7.1", 8080, "10.10.7.2", 8080, sys.argv[1]))
    t_server.daemon = True
    t_server.start()
    t_server.join()
    
main()
