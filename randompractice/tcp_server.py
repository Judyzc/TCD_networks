# SERVER 
import socket

TCP_IP = "0.0.0.0"  # Listen on all interfaces
TCP_PORT = 5005     # Port to listen on
BUFFER_SIZE = 1024  # Buffer size for receiving data

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((TCP_IP, TCP_PORT))
server_socket.listen(1)  # Listen for incoming connections (1 connection at a time)

print(f"TCP server listening on {TCP_IP}:{TCP_PORT}")

# Accept a connection
conn, addr = server_socket.accept()
print(f"Connected by {addr}")

while True:
    data = conn.recv(BUFFER_SIZE)
    if not data:
        break  # Connection closed by client
    print(f"Received: {data.decode()}")
    # Optionally, you could send a response back
    conn.sendall(data)  # Echo back the received data

conn.close()