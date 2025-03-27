# UDP SERVER 
import socket

print("hello world")

UDP_IP = "0.0.0.0"  # Listen on localhost (change as needed)
UDP_PORT = 5005       # Port to listen on

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"UDP server listening on {UDP_IP}:{UDP_PORT}")

while True:
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    print(f"Received message from {addr}: {data.decode()}")