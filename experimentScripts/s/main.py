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
            start = time.time()
            client_socket.sendto(dummy_packet, (dst_ip, dst_port))
            end, _ = client_socket.recvfrom(1024)
            end = float(end)
            end_to_end_delays.append(end - start)

def main():
    global N, M
    N = int(sys.argv[1]) / M
    exp_name = sys.argv[2]
    N = 1 if N == 0 else int(np.ceil(N))
    t_client = threading.Thread(target=client, args=("10.10.3.1", 8080, "10.10.3.2", 8080))
    t_client.start()
    t_client.join()
    termination_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    termination_socket.sendto("!".encode(), ("10.10.3.2", 7070))
    out = "N = " + str(N * M) + "\n" + "Mean = " + str(np.mean(end_to_end_delays)) + "\n" + "Standard Deviation = " + str(np.std(end_to_end_delays)) + "\n"
    f = open(exp_name + ".txt", "w+")
    f.write(out)
    f.close()
    print(out)

main()
