import threading
import socket
import time

def server(src_ip, src_port, dst_ip, dst_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    server_socket.bind((src_ip, src_port))
    while True:
        data, addr = server_socket.recvfrom(1024)
        server_socket.sendto(data, (dst_ip, dst_port))

def main():
    t_server_from_s_to_d = threading.Thread(target=server, args=("10.10.3.2", 8080, "10.10.7.1", 8080))
    t_server_from_d_to_s = threading.Thread(target=server, args=("10.10.7.2", 8080, "10.10.3.1", 8080))
    t_server_from_s_to_d.daemon = True
    t_server_from_d_to_s.daemon = True
    t_server_from_s_to_d.start()
    t_server_from_d_to_s.start()
    termination_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    termination_socket.bind(("10.10.3.2", 7070))
    termination_socket.recvfrom(1024)
    termination_socket.sendto("!".encode(), ("10.10.7.1", 7070))

main()
