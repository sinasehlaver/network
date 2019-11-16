import socket
import threading
import ntplib
import time

def server(src_ip, src_port, dst_ip, dst_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((src_ip, src_port))
    base = ntplib.NTPClient().request('pool.ntp.org').tx_time
    local = time.time()
    delta = base - local
    while True:
        server_socket.recvfrom(1024)
        e = time.time()
        e += delta
        server_socket.sendto(str(e).encode(), (dst_ip, dst_port))

def main():
    t_server = threading.Thread(target=server, args=("10.10.7.1", 8080, "10.10.7.2", 8080))
    t_server.start()
    t_server.join()

main()