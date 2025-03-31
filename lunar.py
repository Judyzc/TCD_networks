import socket
import time
import random
import threading
from rover_control import execute_movement
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel

# UDP Sockets for telemetry and commands
UPDATES_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SENSOR_DATA_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
COMMAND_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

COMMAND_SOCKET.bind((LUNAR_IP, LUNAR_RECEIVE_PORT))

def send_packet(packet, socket, address):
    """Send a LunarPacket using UDP."""
    try:
        packet_data = packet.build()
        not_lost = channel.send_w_delay_loss(socket, packet_data, address)
        if not_lost:
            print(f"[LUNAR] ID={packet.packet_id} *SENT*")
        else:
            print(f"[LUNAR] Packet ID={packet.packet_id} *LOST*")
    except socket.error as e:
        print(f"[ERROR] Failed to send packet: {e}")

def send_temperature(packet_id, address):
    """Send temperature data packet."""
    temp_data = round(random.uniform(-150, 130), 2)
    packet = LunarPacket(
        packet_id=packet_id,
        packet_type=0,  # Temperature
        data=temp_data
    )
    send_packet(packet, SENSOR_DATA_SOCKET, address)

def send_system_status(packet_id, address):
    """Send system status data."""
    battery = round(random.uniform(10, 100), 2)
    sys_temp = round(random.uniform(-40, 80), 2)
    status_data = battery + (sys_temp / 1000)
    packet = LunarPacket(
        packet_id=packet_id,
        packet_type=1,  # System Status
        data=status_data
    )
    send_packet(packet, UPDATES_SOCKET, address)

def send_data():
    """Continuously send telemetry data."""
    temp_packet_id = 0
    status_packet_id = 1000

    while True:
        send_temperature(temp_packet_id, (EARTH_IP, EARTH_RECEIVE_SENSOR_DATA_PORT))
        send_system_status(status_packet_id, (EARTH_IP, EARTH_RECEIVE_UPDATES_PORT))

        temp_packet_id = (temp_packet_id + 1) % 1000
        status_packet_id = 1000 + ((status_packet_id + 1 - 1000) % 1000)

        time.sleep(5)

def command_server():
    """Handle incoming commands via UDP."""
    print(f"[MOON] Command server ready on UDP port {LUNAR_RECEIVE_PORT}")
    while True:
        try:
            data, addr = COMMAND_SOCKET.recvfrom(1024)
            if addr[0] != EARTH_IP:
                continue
                
            cmd = data.decode().strip()
            print(f"[MOON] Received command: {cmd}")
            execute_movement(cmd)

            # Send ACK back to Earth
            ack_message = f"ACK-{cmd}".encode()
            COMMAND_SOCKET.sendto(ack_message, (EARTH_IP, EARTH_COMMAND_PORT))
            print(f"[MOON] ACK Sent for {cmd}")

        except Exception as e:
            print(f"[MOON] Command error: {e}")

if __name__ == "__main__":
    threading.Thread(target=command_server, daemon=True).start()
    send_data()
