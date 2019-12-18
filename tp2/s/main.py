import socket
import threading
import struct
import sys
import time
import hashlib
import os

payload_size = 512
N = 5*1024*1024//payload_size

base = 0
window_size = 8

is_acked = [False] * (N + 1)
is_sent = [False] * N
byte_chunks = ["".encode()] * (N + 1)

timeout_value = 1

consecutive_timeouts = 0
consecutive_timeouts_lock = threading.Lock()
consecutive_timeouts_threshold = N//10

def calculate_checksum(payload):
    return hashlib.md5(payload).hexdigest().encode()

def create_packet(seq_n, ack_n, payload="".encode()):
    checksum = calculate_checksum(payload)
    length = 38 + len(payload)
    return struct.pack("!HHH", seq_n, ack_n, length) + checksum + payload

def extract_packet(packet):
    return (*struct.unpack("!HHH", packet[:6]), packet[6:38], packet[38:])

def divide_into_byte_chunks(file_name):
    global payload_size, N, byte_chunks
    f = open(file_name, "rb")
    content = f.read()
    f.close()
    for i in range(N):
        byte_chunks[i] = content[i*payload_size : (i + 1)*payload_size]

def file_sender(src_ip, src_port, dst_ip, dst_port):
    global N, base, window_size, is_acked, is_sent, byte_chunks, consecutive_timeouts, consecutive_timeouts_lock, consecutive_timeouts_threshold
    threading.Thread(target=ack_receiver, daemon=True, args=(src_ip, src_port)).start()
    file_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    reached_end = False
    while not all(is_acked[:-1]):
        consecutive_timeouts_lock.acquire()
        if consecutive_timeouts > consecutive_timeouts_threshold:
            return
        consecutive_timeouts_lock.release()
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
                threading.Thread(target=sender, daemon=True, args=(file_sender_socket, dst_ip, dst_port, i)).start()
                is_sent[i] = True
    sender(file_sender_socket, dst_ip, dst_port, -1)

def ack_receiver(src_ip, src_port):
    global is_acked
    ack_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack_receiver_socket.bind((src_ip, src_port))
    while not all(is_acked):
        packet, _ = ack_receiver_socket.recvfrom(1024)
        seq_n, ack_n, _, _, _ = extract_packet(packet)
        if ack_n == 0:
            is_acked = [True] * (N + 1)
        else:
            is_acked[ack_n - 1] = True

def sender(file_sender_socket, dst_ip, dst_port, i):
    global is_acked, byte_chunks, timeout_value, consecutive_timeouts, consecutive_timeouts_lock
    is_timedout = False
    while not is_acked[i]:
        if is_timedout:
            consecutive_timeouts_lock.acquire()
            consecutive_timeouts += 1
            consecutive_timeouts_lock.release()
        file_sender_socket.sendto(create_packet(i + 1, 0, byte_chunks[i]), (dst_ip, dst_port))
        time.sleep(timeout_value)
        is_timedout = True
    consecutive_timeouts_lock.acquire()
    consecutive_timeouts = 0
    consecutive_timeouts_lock.release()

def exp1():
    divide_into_byte_chunks("input1")
    file_sender("10.10.3.1", 8080, "10.10.3.2", 8080)

def exp2():
    divide_into_byte_chunks("input2")
    # fork it
    pid = os.fork()
    if pid == 0:
        # child, r1
        file_sender("10.10.1.1", 8080, "10.10.1.2", 8080)
    else:
        # parent, r2
        file_sender("10.10.2.2", 8080, "10.10.2.1", 8080)
        os.waitpid(pid)

def main():
    if sys.argv[1] == "exp1":
        exp1()
    elif sys.argv[1] == "exp2":
        exp2()

main()
