import socket
import time

nodes = [("10.10.8.1", 8080)]
n = 1

rtts = []

for i in range(n):
    acc = 0
    for j in range(1000):
        packet = str(j).encode()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        start = time.time()
        client_socket.sendto(packet, nodes[i])
        data, addr = client_socket.recvfrom(1024)
        end = time.time()
        acc += end - start
    rtts.append(acc)
print(rtts)
