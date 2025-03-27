import socket

print("hello world")

UDP_IP = "10.6.103.251"  # Target IP (should match the server IP)
UDP_PORT = 5005       # Target port (should match the server port)
MESSAGE = "Hi, this is Judy!"

# # Create UDP socket
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))


# # Create TCP socket
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# try:
#     sock.connect((TCP_IP, TCP_PORT))
#     sock.send(MESSAGE.encode())
# finally:
#     sock.close()

import socket

TCP_IP = "10.6.103.251"  # Replace with the server's network IP address
TCP_PORT = 5005       # Must match the server's port
BUFFER_SIZE = 1024    # Buffer size for receiving data
MESSAGE = "THIS IS JUDY!"

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((TCP_IP, TCP_PORT))

client_socket.sendall(MESSAGE.encode())
data = client_socket.recv(BUFFER_SIZE)

print(f"Received from server: {data.decode()}")
client_socket.close()
