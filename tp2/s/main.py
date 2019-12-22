import socket
import threading
import struct
import sys
import time
import hashlib
import statistics as st
import math

if sys.argv[1] == "exp1":
    dst_ips = ["10.10.3.2", "10.10.3.2"]
elif sys.argv[1] == "exp2":
    dst_ips = ["10.10.1.2", "10.10.2.1"]
else:
    sys.exit()

payload_size = 512
N = 5*1024*1024//payload_size
window_size = 32
byte_chunks = ["".encode()]*(N + 1)

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

def file_sender():
    global dst_ips, payload_size, N, base, window_size, is_acked, is_sent, byte_chunks, timeout_interval, estimated_rtt, dev_rtt, timeout_interval, estimated_rtt, timeout_interval_lock, starts, is_timedout, is_timedout_lock, timeouts
    file_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    reached_end = False
    file_transfer_time_start = time.time()
    while not all(is_acked[:-1]):
        is_timedout_lock.acquire()
        if is_timedout:
            is_timedout = False
            for i in timeouts:
                key = i % 2
                if dst_ips[key] != dst_ips[(key + 1) % 2]:
                    dst_ips[key] = dst_ips[(key + 1) % 2]
                    timeout_interval[key] = timeout_interval[(key + 1) % 2]
                    estimated_rtt[key] = estimated_rtt[(key + 1) % 2]
                    dev_rtt[key] = dev_rtt[(key + 1) % 2]
                threading.Thread(target=sender, daemon=True, args=(file_sender_socket, i)).start()
            timeouts.clear()
        is_timedout_lock.release()
        if not reached_end:
            for i in range(base, base + window_size):
                if is_acked[i]:
                    if base + window_size + 1 <= N:
                        base += 1
                    else:
                        reached_end = True
                        break
                else:
                    break
        for i in range(base, base + window_size):
            if not is_sent[i]:
                threading.Thread(target=sender, daemon=True, args=(file_sender_socket, i)).start()
                is_sent[i] = True
    file_transfer_time_end = time.time()
    sender(file_sender_socket, -1)
    return file_transfer_time_end - file_transfer_time_start

def ack_receiver():
    global dst_ips, payload_size, N, base, window_size, is_acked, is_sent, byte_chunks, timeout_interval, estimated_rtt, dev_rtt, timeout_interval, estimated_rtt, timeout_interval_lock, starts, is_timedout, is_timedout_lock, timeouts
    ack_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack_receiver_socket.bind(("0.0.0.0", 8080))
    while not all(is_acked):
        packet, _ = ack_receiver_socket.recvfrom(1024)
        end = time.time()
        seq_n, ack_n, _, _, _ = extract_packet(packet)
        i = ack_n - 1
        is_acked[ack_n - 1] = True
        key = i % 2 if dst_ips[0] != dst_ips[1] else 0
        sample_rtt = end - starts[i]
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

def sender(file_sender_socket, i):
    global dst_ips, payload_size, N, base, window_size, is_acked, is_sent, byte_chunks, timeout_interval, estimated_rtt, dev_rtt, timeout_interval, estimated_rtt, timeout_interval_lock, starts, is_timedout, is_timedout_lock, timeouts
    send_count = 0
    key = i % 2 if dst_ips[0] != dst_ips[1] else 0
    f = False
    while not is_acked[i]:
        is_timedout_lock.acquire()
        if send_count >= 100:
            is_timedout = True
            timeouts.append(i)
            f = True
        is_timedout_lock.release()
        if f:
            return
        timeout_interval_lock[key].acquire()
        timeout_value = timeout_interval[key]
        timeout_interval_lock[key].release()
        starts[i] = time.time()
        file_sender_socket.sendto(create_packet(i + 1, 0, byte_chunks[i]), (dst_ips[key], 8080))
        time.sleep(timeout_value)
        send_count += 1

def init():
    global dst_ips, payload_size, N, base, window_size, is_acked, is_sent, byte_chunks, timeout_interval, estimated_rtt, dev_rtt, timeout_interval, estimated_rtt, timeout_interval_lock, starts, is_timedout, is_timedout_lock, timeouts
    base = 0
    is_acked = [False]*(N + 1)
    is_sent = [False]*N
    timeout_interval = [0.05, 0.05]
    estimated_rtt = [None, None]
    dev_rtt = [None, None]
    timeout_interval_lock = [threading.Lock(), threading.Lock()]
    starts = [None]*(N + 1)
    is_timedout = False
    is_timedout_lock = threading.Lock()
    timeouts = []

def sample():
    init()
    threading.Thread(target=ack_receiver, daemon=True).start()
    return file_sender()

def main():
    if sys.argv[1] == "exp1":
        divide_into_byte_chunks("input1")
    elif sys.argv[1] == "exp2":
        divide_into_byte_chunks("input2")
    ftts = []
    error = 1
    ftts.append(sample())
    print(len(ftts), error, ftts[-1])
    while error >= 0.025:
        ftts.append(sample())
        error = 1.96*st.stdev(ftts)/math.sqrt(len(ftts))
        print(len(ftts), error, ftts[-1])
    print("size = ", len(ftts))
    print("mean = ", st.mean(ftts))
    print("standard deviation = ", st.stdev(ftts))
    print("margin of error = ", error)
    print("median = ", st.median(ftts))

main()
