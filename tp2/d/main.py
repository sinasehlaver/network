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

def create_packet(seq_n, ack_n, payload="".encode()):
    checksum = calculate_checksum(payload)
    length = 8 + len(payload)
    return struct.pack("!HHHH", checksum, length, seq_n, ack_n) + payload

def file_receiver(src_ip, src_port, dst_ip, dst_port, file_name):
    byte_chunks = []
    expected_seq_n = 1
    last_ack_packet = create_packet(0, 0)
    file_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    file_receiver_socket.bind((src_ip, src_port))
    ack_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        if expected_seq_n == 10241:
            break
        packet, _ = file_receiver_socket.recvfrom(1024)
        (checksum, length, seq_n, ack_n), payload = struct.unpack("!HHHH", packet[:8]), packet[8:]
        if seq_n == expected_seq_n and checksum == calculate_checksum(payload):
            byte_chunks.append(payload)
            expected_seq_n += 1
            last_ack_packet = create_packet(0, seq_n)
            ack_sender_socket.sendto(last_ack_packet, (dst_ip, dst_port))
        else:
            ack_sender_socket.sendto(last_ack_packet, (dst_ip, dst_port))
    f = open(file_name, "wb+")
    f.writelines(byte_chunks)
    f.close()

def main():
    t_server = threading.Thread(target=file_receiver, args=("10.10.7.1", 8080, "10.10.7.2", 8080, sys.argv[1]))
    t_server.daemon = True
    t_server.start()
    t_server.join()
    
main()
