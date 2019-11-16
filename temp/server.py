import socket
import threading

def server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    server_socket.bind((ip, port))
    while True:
        data, addr = server_socket.recvfrom(1024)
        server_socket.sendto(data, addr)

def main():
    t_server_r1 = threading.Thread(target=server, args=("10.10.1.1", 8080))
    t_server_r2 = threading.Thread(target=server, args=("10.10.2.2", 8080))
    t_server_r3 = threading.Thread(target=server, args=("10.10.3.1", 8080))
    t_server_r1.start()
    t_server_r2.start()
    t_server_r3.start()
    t_server_r1.join()
    t_server_r2.join()
    t_server_r3.join()

main()