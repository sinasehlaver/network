import socket
import threading
import struct
import sys
import hashlib

payload_size = 512
N = 5*1024*1024//payload_size

done = False

byte_chunks = [None] * N

def calculate_checksum(payload):
    return hashlib.md5(payload).hexdigest().encode()

def create_packet(seq_n, ack_n, payload="".encode()):
    checksum = calculate_checksum(payload)
    length = 38 + len(payload)
    return struct.pack("!HHH", seq_n, ack_n, length) + checksum + payload

def extract_packet(packet):
    return (*struct.unpack("!HHH", packet[:6]), packet[6:38], packet[38:])

def file_receiver(src_ip, src_port, dst_ip, dst_port):
    global done, byte_chunks, byte_chunks_locks
    file_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    file_receiver_socket.bind((src_ip, src_port))
    ack_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        if done:
            ack_sender_socket.sendto(create_packet(0, 0), (dst_ip, dst_port))
            return
        packet, _ = file_receiver_socket.recvfrom(1024)
        seq_n, ack_n, _, checksum, payload = extract_packet(packet)
        if seq_n == 0 and ack_n == 0:
            done = True
            ack_sender_socket.sendto(create_packet(0, 0), (dst_ip, dst_port))
            return
        if checksum == calculate_checksum(payload):
            if byte_chunks[seq_n - 1] == None:
                byte_chunks[seq_n - 1] = payload
            ack_sender_socket.sendto(create_packet(0, seq_n), (dst_ip, dst_port))

def write_to_file(file_name):
    global byte_chunks
    f = open(file_name, "wb+")
    f.writelines(byte_chunks)
    f.close()

def exp1():
    t_file_receiver = threading.Thread(target=file_receiver, args=("10.10.7.1", 8080, "10.10.7.2", 8080))
    t_file_receiver.start()
    t_file_receiver.join()
    write_to_file("output1")

def exp2():
    global byte_chunks
    t_file_receiver_r1 = threading.Thread(target=file_receiver, daemon=True, args=("10.10.4.2", 8080, "10.10.8.1", 8080))
    t_file_receiver_r2 = threading.Thread(target=file_receiver, daemon=True, args=("10.10.5.2", 8080, "10.10.8.2", 8080))
    t_file_receiver_r1.start()
    t_file_receiver_r2.start()
    while not done:
        continue
    write_to_file("output2")

def main():
    if sys.argv[1] == "exp1":
        exp1()
    elif sys.argv[1] == "exp2":
        exp2()
    
main()
