import socket
import threading
import time
import subprocess as sp
import numpy as np
import sys

N = 0
M = 1000
end_to_end_delays = []

def client(src_ip, src_port, dst_ip, dst_port):
    global N, M, end_to_end_delays
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind((src_ip, src_port))
    sync_packet = "!".encode()
    dummy_packet = ".".encode()
    for i in range(N):
        sp.call("sudo ntpdate -u pool.ntp.org", shell=True)
        client_socket.sendto(sync_packet, (dst_ip, dst_port))
        client_socket.recvfrom(1024)
        for j in range(M):
            s = time.time()
            client_socket.sendto(dummy_packet, (dst_ip, dst_port))
            e, _ = client_socket.recvfrom(1024)
            e = float(e)
            end_to_end_delays.append(e - s)

def main():
    global N, M
    N = int(sys.argv[1]) / M
    N = 1 if N == 0 else np.ceil(N)
    t_client = threading.Thread(target=client, args=("10.10.3.1", 8080, "10.10.3.2", 8080))
    t_client.start()
    t_client.join()
    print(np.mean(end_to_end_delays))
    print(np.std(end_to_end_delays))
    termination_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    termination_socket.sendto("!".encode(), ("10.10.3.2", 7070))

main()
