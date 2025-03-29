import socket
import time
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel

def send_ack(packet_id, conn):
    """Return ACK for Lunar Packet to Moon w/ random loss."""

    ack_message = str(packet_id)
    not_dropped = channel.send_w_delay_loss(conn, ack_message.encode()) # actual sending is done in the channel_send_w_dalay_loss function
    if not_dropped:
        print(f"[EARTH] Sent ACK for Packet {packet_id}")
    else: 
        print(f"[EARTH] LOST ACK for Packet {packet_id}")


def parse_system_status(data):
    """Extract battery and system temperature from a LunarPacket."""

    battery = int(data)  # Extract integer part as battery
    sys_temp = (data - battery) * 1000 - 40  # Extract decimal part and shift back
    return battery, sys_temp


def receive_packet():
    """Receive Lunar Packets from Moon through TCP with a persistent connection."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((EARTH_IP, EARTH_PORT))
        s.listen(5)  # Allow multiple connections
        print("[EARTH] Waiting for connection...")

        while True:
            conn, addr = s.accept()
            print(f"[EARTH] Connection established with {addr}")
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break  # Exit inner loop if connection is closed
                    packet_id, packet_type, data, timestamp = LunarPacket.parse(data)

                    if packet_type == 0:  # Temperature, data is temp
                        print(f"Received Temperature: {data}°C. Packet ID: {packet_id}, Timestamp: {timestamp}")

                    elif packet_type == 1:  # System status
                        battery, sys_temp = parse_system_status(data)
                        print(f"Received System Status - Battery: {battery}%, System Temp: {sys_temp}°C. Packet ID: {packet_id}, Timestamp: {timestamp}")

                    # print(f"[EARTH] Received -> ID: {packet_id}, Type: {packet_type}, Data: {data:.2f}, Timestamp: {timestamp}")
                    send_ack(packet_id, conn)  # Send ACK for received packet


if __name__ == "__main__":
    receive_packet()
