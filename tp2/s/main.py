import socket
import threading
import struct
import sys
import time

payload_size = 512
N = 5*1024*1024//payload_size

base = 0
window_size = 8

is_acked = [False] * N
is_sent = [False] * N
byte_chunks = []

timeout_value = 1

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

def divide_into_byte_chunks(file_name):
    global payload_size, N, byte_chunks
    f = open(file_name, "rb")
    content = f.read()
    f.close()
    for i in range(N):
        byte_chunks.append(content[i*payload_size : (i + 1)*payload_size])

def file_sender(dst_ip, dst_port):
    global N, base, window_size, is_acked, is_sent, byte_chunks
    file_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    reached_end = False
    while not all(is_acked):
        if not reached_end:
            for i in range(base, base + window_size):
                if is_acked[i]:
                    if base + window_size + 1 <= N:
                        base += 1
                    else:
                        reached_end = True
                        break
        for i in range(base, base + window_size):
            if not is_sent[i]:
                threading.Thread(target=sender, args=(file_sender_socket, dst_ip, dst_port, i)).start()
                is_sent[i] = True
    file_sender_socket.sendto(create_packet(0, 0), (dst_ip, dst_port))

def ack_receiver(src_ip, src_port):
    global is_acked
    ack_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack_receiver_socket.bind((src_ip, src_port))
    while not all(is_acked):
        packet, _ = ack_receiver_socket.recvfrom(1024)
        _, _, _, ack_n = struct.unpack("!HHHH", packet[:8])
        is_acked[ack_n - 1] = True

def sender(file_sender_socket, dst_ip, dst_port, i):
    global is_acked, byte_chunks, timeout_value
    while not is_acked[i]:
        file_sender_socket.sendto(create_packet(i + 1, 0, byte_chunks[i]), (dst_ip, dst_port))
        time.sleep(timeout_value)

def main():
    divide_into_byte_chunks(sys.argv[1])
    t_file_sender = threading.Thread(target=file_sender, args=("10.10.3.2", 8080))
    t_ack_receiver = threading.Thread(target=ack_receiver, args=("10.10.3.1", 8080))
    t_file_sender.start()
    t_ack_receiver.start()
    t_file_sender.join()
    t_ack_receiver.join()

main()
