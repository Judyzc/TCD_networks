import threading
import socket
import time
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel

def send_ack(packet_id, conn):
    """Send ACK for received Lunar Packet."""
    ack_message = str(packet_id)
    not_dropped = channel.send_w_delay_loss(conn, ack_message.encode())
    if not_dropped:
        print(f"[EARTH] Sent ACK for Packet {packet_id}")
    else:
        print(f"[EARTH] LOST ACK for Packet {packet_id}")

def receive_packet():
    """Receives telemetry data from the Lunar Rover."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((EARTH_IP, EARTH_RECEIVE_PORT))
        s.listen(5)
        print("[EARTH] Waiting for telemetry data...")

        while True:
            conn, addr = s.accept()
            print(f"[EARTH] Connected to Lunar Rover at {addr}")
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break  # Exit loop if connection closes
                    packet_id, packet_type, data, timestamp = LunarPacket.parse(data)

                    if packet_type == 0:
                        print(f"Received Temperature: {data:.2f}°C (Packet ID: {packet_id})")
                    elif packet_type == 1:
                        battery, sys_temp = int(data), round((data - int(data)) * 1000 - 40, 4)
                        print(f"System Status: Battery={battery}%, Temp={sys_temp:.2f}°C (Packet ID: {packet_id})")
                    elif packet_type == 2:
                        print(f"Received Movement Confirmation: {data} (Packet ID: {packet_id})")

                    send_ack(packet_id, conn)

def send_movement_command():
    """Sends movement commands to the Lunar Rover."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((LUNAR_IP, LUNAR_RECEIVE_PORT))  # Connect to Lunar's movement command port
        packet_id = 2000

        while True:
            command = input("Enter command (FORWARD, BACKWARD, LEFT, RIGHT, STOP): ").strip().upper()
            if command in ["FORWARD", "BACKWARD", "LEFT", "RIGHT", "STOP"]:
                packet = LunarPacket(packet_id=packet_id, packet_type=2, data=command)
                channel.send_w_delay_loss(s, packet.build())
                print(f"[EARTH] Sent Command: {command} (Packet ID: {packet_id})")
                packet_id += 1
            else:
                print("Invalid command. Try again.")

# Run both functions in parallel
if __name__ == "__main__":
    recv_thread = threading.Thread(target=receive_packet, daemon=True)
    send_thread = threading.Thread(target=send_movement_command, daemon=True)

    recv_thread.start()
    send_thread.start()

    recv_thread.join()
    send_thread.join()
