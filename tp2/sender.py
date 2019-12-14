# importing socket module 
import socket 
  
UDP_IP = "localhost"
UDP_PORT = 8080
MESSAGE = "GeeksforGeeks"
  
print ("message:", MESSAGE) 
  
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
sock.sendto(bytes(MESSAGE, "utf-8"), (UDP_IP, UDP_PORT))