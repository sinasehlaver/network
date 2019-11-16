import threading
import socket
import time
import sys

rtts = {"r1": 0, "r3": 0, "s": 0, "d": 0}

def server_r1(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))
    data, addr = server_socket.recvfrom(1024)

def server_r3(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))
    data, addr = server_socket.recvfrom(1024)

def client(name, ip, port, N):
    global rtts
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if (name == "r1" or name == "r3"):
        client_socket.sendto("!".encode(), (ip, port))
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
    t_server_r1 = threading.Thread(target=server_r1, args=("10.10.5.1", 7070))
    t_server_r3 = threading.Thread(target=server_r3, args=("10.10.6.1", 7070))
    t_r1 = threading.Thread(target=client, args=("r1", "10.10.4.1", 8080, N))
    t_r3 = threading.Thread(target=client, args=("r3", "10.10.6.2", 8080, N))
    t_s = threading.Thread(target=client, args=("s", "10.10.2.2", 8080, N))
    t_d = threading.Thread(target=client, args=("d", "10.10.5.2", 8080, N))
    t_server_r1.start()
    t_server_r3.start()
    t_r1.start()
    t_r3.start()
    t_s.start()
    t_d.start()
    t_s.join()
    t_d.join()
    t_r1.join()
    t_r3.join()
    f = open("link_costs.txt", "w+")
    for i in rtts:
        out = "r2 - " + i + " = " + str(rtts[i])
        print(out)
        f.write(out + "\n")
    f.close()
    t_server_r1.join()
    t_server_r3.join()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto("!".encode(), ("10.10.4.1", 7070))
    s.sendto("!".encode(), ("10.10.6.2", 7070))
    s.sendto("!".encode(), ("10.10.2.2", 7070))
    s.sendto("!".encode(), ("10.10.5.2", 7070))


main()

