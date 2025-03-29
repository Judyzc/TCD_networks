# TCP CLIENT 
import socket

TCP_IP = "172.20.10.2"  # Replace with the server's network IP address
TCP_PORT = 5005       # Must match the server's port
BUFFER_SIZE = 1024    # Buffer size for receiving data
MESSAGE = "HELLO !!!"

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((TCP_IP, TCP_PORT))

client_socket.sendall(MESSAGE.encode())
data = client_socket.recv(BUFFER_SIZE)

print(f"Received from server: {data.decode()}")
client_socket.close()