import socket
import threading
import struct

def server(src_ip, src_port, dst_ip, dst_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((src_ip, src_port))
    while True:
        packet, _ = server_socket.recvfrom(1024)
        (checksum, length, seq_n, ack_n), payload = struct.unpack("!HHHH", packet[:8]), packet[8:]
        print(checksum, length, seq_n, ack_n, payload)

def main():
    t_server = threading.Thread(target=server, args=("10.10.7.1", 8080, "10.10.7.2", 8080))
    t_server.daemon = True
    t_server.start()
    t_server.join()
    
main()
