import socket
import time
import random
from lunar_packet import LunarPacket
from env_variables import *

def send_packet(packet):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((EARTH_IP, EARTH_PORT))  # Connect to Earth
        s.sendall(packet.build())  # Send the built packet
        print(f"[LUNAR] Sent Packet ID={packet.packet_id}, Data={packet.data:.2f}")

def receive_ack():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((LUNAR_IP, LUNAR_PORT))  # Bind to Lunar IP
        s.listen(1)  # Listen for 1 connection (TCP)
        print("[LUNAR] Waiting for ACK...")
        conn, addr = s.accept()  # Accept a connection
        with conn:
            data = conn.recv(1024)
            print(f"[LUNAR] Received ACK: {data.decode()}")

if __name__ == "__main__":
    for i in range(5):  # Send 5 packets
        data = round(random.uniform(-50, 50), 2)
        packet = LunarPacket(packet_id=i, packet_type=0, data=data)
        send_packet(packet)
        time.sleep(1)

    receive_ack()  # Keep listening for ACKs
