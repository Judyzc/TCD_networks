import socket
import time
from lunar_packet import LunarPacket

EARTH_IP = "192.168.1.102"  # This machine's IP
LUNAR_IP = "192.168.1.101"  # Laptop A's IP
EARTH_PORT = 5000
LUNAR_PORT = 6000  # Send ACKs to Lunar

def receive_packet():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((EARTH_IP, EARTH_PORT))  # Bind to Earth IP
        s.listen(1)  # Listen for 1 connection (TCP)
        print("[EARTH] Waiting for connection...")
        conn, addr = s.accept()  # Accept a connection
        with conn:
            print(f"[EARTH] Connection established with {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                packet_id, packet_type, temperature, timestamp, is_valid = LunarPacket.parse(data)

                print(f"[EARTH] Received -> ID: {packet_id}, Temp: {temperature:.2f}°C, Checksum Valid: {is_valid}")

                send_ack(packet_id, conn)

def send_ack(packet_id, conn):
    ack_message = f"ACK for Packet {packet_id}"
    conn.sendall(ack_message.encode())
    print(f"[EARTH] Sent ACK for Packet {packet_id}")

if __name__ == "__main__":
    receive_packet()
