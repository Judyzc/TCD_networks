import socket
from lunar_packet import LunarPacket

EARTH_PORT = 5000
LUNAR_IP = "127.0.0.1"
LUNAR_PORT = 6000  # Send acknowledgments back to Lunar

def receive_packet():
    """Listen for packets from the lunar rover."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("127.0.0.1", EARTH_PORT))
        while True:
            data, addr = s.recvfrom(1024)
            packet_id, packet_type, temperature, timestamp, is_valid = LunarPacket.parse(data)

            print(f"[EARTH] Received -> ID: {packet_id}, Temp: {temperature:.2f}°C, Checksum Valid: {is_valid}")

            send_ack(packet_id, addr)  # Send acknowledgment back to lunar rover

def send_ack(packet_id, addr):
    """Send an acknowledgment back to the lunar rover."""
    ack_message = f"ACK for Packet {packet_id}"
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(ack_message.encode(), (LUNAR_IP, LUNAR_PORT))
    print(f"[EARTH] Sent ACK for Packet {packet_id}")

if __name__ == "__main__":
    receive_packet()
