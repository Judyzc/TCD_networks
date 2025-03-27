import socket
import time
import random
from lunar_packet import LunarPacket

EARTH_IP = "127.0.0.1"
EARTH_PORT = 5000
LUNAR_PORT = 6000  # Listening port for acknowledgments

def send_packet(packet):
    """Send a packet to Earth."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(packet.build(), (EARTH_IP, EARTH_PORT))
        print(f"[LUNAR] Sent Packet ID={packet.packet_id}, Temp={packet.temperature:.2f}°C")

def receive_ack():
    """Listen for acknowledgments from Earth."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("127.0.0.1", LUNAR_PORT))
        while True:
            data, addr = s.recvfrom(1024)
            print(f"[LUNAR] Received ACK from {addr}: {data.decode()}")

if __name__ == "__main__":
    for i in range(5):  # Send 5 packets
        temp = round(random.uniform(-50, 50), 2)
        packet = LunarPacket(packet_id=i, packet_type=0, temperature=temp)
        send_packet(packet)
        time.sleep(1)  # Simulated time gap

    receive_ack()  # Keep listening for ACKs
