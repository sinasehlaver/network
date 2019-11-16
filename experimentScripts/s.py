import socket
import threading
import ntplib
import time


def client(src_ip, src_port, dst_ip, dst_port):
    N = 10000
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind((src_ip, src_port))
    acc = 0
    base = ntplib.NTPClient().request('pool.ntp.org').tx_time
    local = time.time()
    delta = base - local
    for i in range(N):
        s = time.time()
        client_socket.sendto("!".encode(), (dst_ip, dst_port))
        e, _ = client_socket.recvfrom(1024)
        e = float(e)
        s += delta
        acc += (e - s)
    print(acc / N)


def main():
    t_client = threading.Thread(target=client, args=("10.10.3.1", 8080, "10.10.3.2", 8080))
    t_client.start()
    t_client.join()

main()