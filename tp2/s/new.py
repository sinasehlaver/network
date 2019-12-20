import socket
import threading
import struct
import sys
import time
import hashlib
import os

src_ips = [None, None]
dst_ips = [None, None]

if sys.argv[1] == "exp1":
    src_ips[0] = "10.10.3.1"
    src_ips[1] = "10.10.3.1"
    dst_ips[0] = "10.10.3.2"
    dst_ips[1] = "10.10.3.2"
elif sys.argv[1] == "exp2":
    src_ips[0] = "10.10.1.1"
    src_ips[1] = "10.10.2.2"
    dst_ips[0] = "10.10.1.2"
    dst_ips[1] = "10.10.2.1"
else:
    sys.exit()

file_sender_socket0 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
file_sender_socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ack_receiver_socket0 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ack_receiver_socket0.bind((src_ips[0], 8080))
if sys.argv[1] == "exp1":
    ack_receiver_socket1 = ack_receiver_socket0
elif sys.argv[1] == "exp2":
    ack_receiver_socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack_receiver_socket1.bind((src_ips[1], 8080))

def send0(seq_n, ack_n, payload):
    global file_sender_socket0, dst_ips
    file_sender_socket0.sendto(create_packet(seq_n, ack_n, payload), (dst_ips[0], 8080))
def send1(seq_n, ack_n, payload):
    global file_sender_socket1, dst_ips
    file_sender_socket1.sendto(create_packet(seq_n, ack_n, payload), (dst_ips[1], 8080))
def receive0():
    global ack_receiver_socket0
    return ack_receiver_socket0.recvfrom(1024)
def receive1():
    global ack_receiver_socket1
    return ack_receiver_socket1.recvfrom(1024)

sends = [send0, send1]
receives = [receive0, receive1]

payload_size = 512
N = 5*1024*1024//payload_size

base = [0, 0]
window_size = [8, 8]

is_acked = [[False] * (N//2 + 1), [False] * (N//2 + 1)]
is_sent = [[False] * (N//2), [False] * (N//2)]
byte_chunks = [["".encode()] * (N//2 + 1), ["".encode()] * (N//2 + 1)]

timeout_interval = [0.05, 0.05]
estimated_rtt = [None, None]
dev_rtt = [None, None]
timeout_interval_lock = [threading.Lock(), threading.Lock()]
starts = [[None] * (N//2 + 1), [None] * (N//2 + 1)]

consecutive_timeouts = [0, 0]
consecutive_timeouts_lock = [threading.Lock(), threading.Lock()]
consecutive_timeouts_threshold = N//20

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
        byte_chunks[i % 2][i//2] = content[i*payload_size : (i + 1)*payload_size]

def file_sender(key):
    global N, base, window_size, is_acked, is_sent, consecutive_timeouts, consecutive_timeouts_lock, consecutive_timeouts_threshold
    threading.Thread(target=ack_receiver, daemon=True, args=(key,)).start()
    reached_end = False
    file_transfer_time_start = time.time()
    while not all(is_acked[key][:-1]):
        consecutive_timeouts_lock[key].acquire()
        if consecutive_timeouts[key] > consecutive_timeouts_threshold:
            src_ips[key] = src_ips[(key + 1) % 2]
            dst_ips[key] = dst_ips[(key + 1) % 2]
            timeout_interval[key] = timeout_interval[(key + 1) % 2]
            estimated_rtt[key] = estimated_rtt[(key + 1) % 2]
            dev_rtt[key] = dev_rtt[(key + 1) % 2]
            consecutive_timeouts[key] = 0
        consecutive_timeouts_lock[key].release()
        if not reached_end:
            for i in range(base[key], base[key] + window_size[key]):
                if is_acked[key][i]:
                    if base[key] + window_size[key] + 1 <= N//2:
                        base[key] += 1
                    else:
                        reached_end = True
                        break
        for i in range(base[key], base[key] + window_size[key]):
            if not is_sent[key][i]:
                print(i, )
                threading.Thread(target=sender, daemon=True, args=(key, i)).start()
                is_sent[key][i] = True
    if all(is_acked[(key + 1) % 2][:-1]):
        file_transfer_time_end = time.time()
        print(file_transfer_time_end - file_transfer_time_start)
        sender(key, -1)
    else:
        window_size[(key + 1) % 2] *= 2
    # Before you leave increase the window size of other's

def ack_receiver(key):
    global is_acked, timeout_interval, estimated_rtt, dev_rtt, timeout_interval_lock, starts
    while not all(is_acked[0] + is_acked[1]):
        packet, _ = receives[key]()
        end = time.time()
        seq_n, ack_n, _, _, _ = extract_packet(packet)
        if ack_n == 0:
            is_acked = [[True] * (N//2 + 1), [True] * (N//2 + 1)]
            return
        key = (ack_n - 1) % 2
        i = (ack_n - 1)//2
        is_acked[key][i] = True
        sample_rtt = end - starts[key][i]
        if estimated_rtt[key] == None:
            estimated_rtt[key] = sample_rtt
        estimated_rtt[key] = 0.875*estimated_rtt[key] + 0.125*sample_rtt
        temp = abs(sample_rtt - estimated_rtt[key])
        if dev_rtt[key] == None:
            dev_rtt[key] = temp
        dev_rtt[key] = 0.75*dev_rtt[key] + 0.25*abs(temp)
        timeout_interval_lock[key].acquire()
        timeout_interval[key] = estimated_rtt[key] + 4*dev_rtt[key]
        timeout_interval_lock[key].release()

def sender(key, i):
    global is_acked, byte_chunks, consecutive_timeouts, consecutive_timeouts_lock, starts, timeout_interval, timeout_interval_lock
    is_timedout = False
    while not is_acked[key][i]:
        if is_timedout:
            consecutive_timeouts_lock[key].acquire()
            consecutive_timeouts[key] += 1
            consecutive_timeouts_lock[key].release()
        timeout_interval_lock[key].acquire()
        timeout_value = timeout_interval[key]
        timeout_interval_lock[key].release()
        starts[key][i] = time.time()
        sends[key](0 if i < 0 else i*2 + key + 1, 0, byte_chunks[key][i])
        time.sleep(timeout_value)
        is_timedout = True
    consecutive_timeouts_lock[key].acquire()
    consecutive_timeouts[key] = 0
    consecutive_timeouts_lock[key].release()

def exp1():
    divide_into_byte_chunks("input1")
    t0 = threading.Thread(target=file_sender, args=(0,))
    t1 = threading.Thread(target=file_sender, args=(1,))
    t0.start()
    t1.start()
    t0.join()
    t1.join()

def exp2():
    divide_into_byte_chunks("input2")
    t0 = threading.Thread(target=file_sender, args=(0,))
    t1 = threading.Thread(target=file_sender, args=(1,))
    t0.start()
    t1.start()
    t0.join()
    t1.join()


def main():
    if sys.argv[1] == "exp1":
        exp1()
    elif sys.argv[1] == "exp2":
        exp2()

main()
