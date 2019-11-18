import socket
import threading
import time
import subprocess as sp

def server(src_ip, src_port, dst_ip, dst_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((src_ip, src_port))
    end_to_end_delays = []
    sync_packet = "!".encode()
    while True:
        packet, _ = server_socket.recvfrom(1024)
        end = time.time()
        if packet == sync_packet:
            sp.call("sudo ntpdate -u pool.ntp.org", shell=True)
        server_socket.sendto(str(end).encode(), (dst_ip, dst_port))

def main():
    t_server = threading.Thread(target=server, args=("10.10.7.1", 8080, "10.10.7.2", 8080))
    t_server.daemon = True
    t_server.start()
    termination_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    termination_socket.bind(("10.10.7.1", 7070))
    termination_socket.recvfrom(1024)

main()
