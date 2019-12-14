import socket
import threading

def checksum(payload):
    s = 0
    for i in range(0, len(payload), 2):
        s += (payload[i] << 8) + payload[i + 1]
        s = (s & 0xffff) + (s >> 16)
    return ~s & 0xffff


def client(src_ip, src_port, dst_ip, dst_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind((src_ip, src_port))
    dummy_packet = ".".encode()
    client_socket.sendto(dummy_packet, (dst_ip, dst_port))

def main():
    t_client = threading.Thread(target=client, args=("10.10.3.1", 8080, "10.10.3.2", 8080))
    t_client.start()
    t_client.join()

main()
