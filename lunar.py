from rover_control import execute_movement
import socket
import time
import random
import threading
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel

# UDP sockets instead of using TCP 
TELEMETRY_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
COMMAND_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
TELEMETRY_SOCKET.settimeout(1)
COMMAND_SOCKET.bind((LUNAR_IP, LUNAR_RECEIVE_PORT))

acknowledged_packets = set() # threading for ACKs to not get hangups
lock = threading.Lock()

def send_packet(packet, address):
    """Send a LunarPacket using UDP."""
    try:
        packet_data = packet.build()
        not_lost = channel.send_w_delay_loss(TELEMETRY_SOCKET, packet_data, address, packet.packet_id)
        if not_lost:
            print(f"[LUNAR] ID={packet.packet_id} *SENT*")
        else:
            print(f"[LUNAR] Packet ID={packet.packet_id} *LOST*")
    except socket.error as e:
        print(f"[ERROR] Failed to send packet: {e}")

def send_packet_with_ack(packet, address):
    """Send a packet and wait for an ACK."""
    send_packet(packet, address)
    start_time = time.time()
    while time.time() - start_time < 5:
        try:
            ack_data, _ = TELEMETRY_SOCKET.recvfrom(1024)
            try:
                ack_id = int(ack_data.decode().strip())
                with lock:
                    acknowledged_packets.add(ack_id)
                if ack_id == packet.packet_id:
                    print(f"[LUNAR] ID={packet.packet_id} *ACK RECVD*\n")
                    return
            except (UnicodeDecodeError, ValueError):
                print(f"[LUNAR] ID={packet.packet_id} *CORRUPTED ACK RECVD*")
        except socket.timeout:
            pass

    print(f"[LUNAR] ID={packet.packet_id} *NO ACK* ->resend\n")
    send_packet_with_ack(packet, address)

def send_temperature(packet_id, address):
    """Send temperature data packet."""
    temp_data = round(random.uniform(-150, 130), 2)
    packet = LunarPacket(
        src_port=LUNAR_SEND_PORT,
        dest_port=EARTH_RECEIVE_PORT,
        packet_id=packet_id,
        packet_type=0,
        data=temp_data
    )
    send_packet_with_ack(packet, address)

def send_system_status(packet_id, address):
    """Send system status data."""
    battery = round(random.uniform(10, 100), 2)
    sys_temp = round(random.uniform(-40, 80), 2)
    status_data = battery + (sys_temp / 1000)
    packet = LunarPacket(
        src_port=LUNAR_SEND_PORT,
        dest_port=EARTH_RECEIVE_PORT,
        packet_id=packet_id,
        packet_type=1,
        data=status_data
    )
    send_packet_with_ack(packet, address)

def send_data():
    """Continuously send telemetry data."""
    temp_packet_id = 0
    status_packet_id = 1000
    address = (EARTH_IP, EARTH_RECEIVE_PORT)

    while True:
        send_temperature(temp_packet_id, address)
        send_system_status(status_packet_id, address)
        
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
            
            # Send ACK back to Earth's command port
            COMMAND_SOCKET.sendto(b"ACK", (EARTH_IP, EARTH_COMMAND_PORT))
            
        except Exception as e:
            print(f"[MOON] Command error: {e}")

if __name__ == "__main__":
    print("""Lunar Rover System Initialised
    Data OUT: {LUNAR_SEND_PORT} → {EARTH_RECEIVE_PORT}
    Commands IN: {EARTH_COMMAND_PORT} → {LUNAR_RECEIVE_PORT}
    """)
    
    # Start command server in a separate thread
    command_thread = threading.Thread(target=command_server, daemon=True)
    command_thread.start()
    
    # Start telemetry transmission in main thread
    send_data()