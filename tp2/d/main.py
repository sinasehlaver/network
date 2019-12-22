import socket
import threading
import struct
import hashlib

dst_ips = {"10.10.3.2":"10.10.7.2", "10.10.1.2":"10.10.8.1", "10.10.2.1":"10.10.8.2"}

payload_size = 512
N = 5*1024*1024//payload_size

byte_chunks = [None]*N

def calculate_checksum(payload):
    return hashlib.md5(payload).hexdigest().encode()

def create_packet(seq_n, ack_n, payload="".encode()):
    checksum = calculate_checksum(payload)
    length = 38 + len(payload)
    return struct.pack("!HHH", seq_n, ack_n, length) + checksum + payload

def extract_packet(packet):
    return (*struct.unpack("!HHH", packet[:6]), packet[6:38], packet[38:])

def file_receiver():
    global dst_ips, payload_size, N, byte_chunks
    file_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    file_receiver_socket.bind(("0.0.0.0", 8080))
    ack_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        packet, (ip, port) = file_receiver_socket.recvfrom(1024)
        seq_n, ack_n, _, checksum, payload = extract_packet(packet)
        if seq_n == 0:
            ack_sender_socket.sendto(create_packet(0, 0), (dst_ips[ip], port))
            return
        if checksum == calculate_checksum(payload):
            if byte_chunks[seq_n - 1] == None:
                byte_chunks[seq_n - 1] = payload
            ack_sender_socket.sendto(create_packet(0, seq_n), (dst_ips[ip], port))

def write_to_file(file_name):
    global dst_ips, payload_size, N, byte_chunks
    f = open(file_name, "wb+")
    f.writelines(byte_chunks)
    f.close()

def sample():
    file_receiver()
    write_to_file("output")
    
def main():
	while True:
		sample()

main()
