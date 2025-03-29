# UDP CLIENT
import socket

print("hello world")

UDP_IP = "172.20.10.2"  # Target IP (should match the server IP)
UDP_PORT = 5005      # Target port (should match the server port)
MESSAGE = "Hi, this is Brandon!"

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
