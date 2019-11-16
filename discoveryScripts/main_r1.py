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
        data, addr = server_socket.recvfrom(1024)
        server_socket.sendto(data, addr)

def client(name, ip, port, N):
    global rtts
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for i in range(N):
        packet = str(i).encode()
        start = time.time()
        client_socket.sendto(packet, (ip, port))
        data, addr = client_socket.recvfrom(1024)
        end = time.time()
        rtts[name] += end - start
    rtts[name] /= N

def main():
    global rtts
    N = int(sys.argv[1])
    lock.acquire()
    t_server = threading.Thread(target=server, args=("10.10.4.1", 8080))
    t_server.daemon = True
    t_server.start()
    lock.acquire()
    lock.release()
    t_s = threading.Thread(target=client, args=("s", "10.10.1.1", 8080, N))
    t_d = threading.Thread(target=client, args=("d", "10.10.4.2", 8080, N))
    t_s.start()
    t_d.start()
    t_s.join()
    t_d.join()
    f = open("link_costs.txt", "w+")
    for i in rtts:
        out = "r1 - " + i + " = " + str(rtts[i])
        print(out)
        f.write(out + "\n")
    f.close()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("10.10.4.1", 7070))
    s.sendto("!".encode(), ("10.10.5.1", 7070))
    s.recvfrom(1024)

main()

