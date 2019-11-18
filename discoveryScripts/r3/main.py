import threading
import socket
import time
import sys

lock = threading.Lock()
rtts = {"s": 0, "d": 0}

def server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    server_socket.bind((ip, port))
    server_socket.recvfrom(1024)
    lock.release()
    while True:
        packet, addr = server_socket.recvfrom(1024)
        server_socket.sendto(packet, addr)

def client(name, ip, port, N):
    global rtts
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dummy_packet = ".".encode()
    for i in range(N):
        start = time.time()
        client_socket.sendto(dummy_packet, (ip, port))
        client_socket.recvfrom(1024)
        end = time.time()
        rtts[name] += (end - start)
    rtts[name] /= N

def main():
    global rtts
    N = int(sys.argv[1])
    lock.acquire()
    t_server = threading.Thread(target=server, args=("10.10.6.2", 8080))
    t_server.daemon = True
    t_server.start()
    lock.acquire()
    lock.release()
    t_client_s = threading.Thread(target=client, args=("s", "10.10.3.1", 8080, N))
    t_client_d = threading.Thread(target=client, args=("d", "10.10.7.1", 8080, N))
    t_client_s.start()
    t_client_d.start()
    t_client_s.join()
    t_client_d.join()
    f = open("link_costs.txt", "w+")
    for i in rtts:
        out = "r3-" + i + " = " + str(rtts[i])
        f.write(out + "\n")
        print(out)
    f.close()
    termination_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    termination_socket.bind(("10.10.6.2", 7070))
    termination_socket.sendto("!".encode(), ("10.10.6.1", 7070))
    termination_socket.recvfrom(1024)

main()
