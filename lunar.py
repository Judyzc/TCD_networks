import socket
import time
import random
import threading
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel
import rover_control  # Movement execution

def send_packet(packet, conn):
    """Send a LunarPacket using an existing connection."""
    try:
        not_lost = channel.send_w_delay_loss(conn, packet.build())
        if not_lost:
            print(f"[LUNAR] Sent Packet ID={packet.packet_id}, Data={packet.data:.2f}")
        else:
            print(f"[LUNAR] LOST Packet ID={packet.packet_id}, Data={packet.data:.2f}")
    except socket.error as e:
        print(f"[ERROR] Failed to send packet: {e}")

def send_packet_with_ack(packet, conn):
    """Send a packet and wait for an ACK."""
    send_packet(packet, conn)
    start_time = time.time()
    while time.time() - start_time < 5:
        try:
            ack_data = conn.recv(1024).decode().strip()
            if ack_data.isdigit() and int(ack_data) == packet.packet_id:
                print(f"[LUNAR] ACK received for Packet ID={packet.packet_id}")
                return
        except socket.timeout:
            pass
    print(f"[LUNAR] No ACK for Packet ID={packet.packet_id}, resending...")
    send_packet(packet, conn)  # Resend if no ACK received

def send_temperature(packet_id, conn):
    """Send temperature data packet."""
    temp_data = round(random.uniform(-150, 130), 2)  # in Celsius
    packet = LunarPacket(packet_id=packet_id, packet_type=0, data=temp_data)
    send_packet_with_ack(packet, conn)

def send_system_status(packet_id, conn):
    """Send system status data (battery + system temperature)."""
    battery = round(random.uniform(10, 100), 2)
    sys_temp = round(random.uniform(-40, 80), 2)
    status_data = battery + (sys_temp / 1000)
    packet = LunarPacket(packet_id=packet_id, packet_type=1, data=status_data)
    send_packet_with_ack(packet, conn)

def send_data():
    """Continuously send telemetry data to Earth."""
    temp_packet_id = 0
    status_packet_id = 1000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
        conn.connect((EARTH_IP, EARTH_RECEIVE_PORT))  # Connect to Earth to send telemetry
        while True:
            send_temperature(temp_packet_id, conn)
            send_system_status(status_packet_id, conn)
            temp_packet_id += 1
            status_packet_id += 1
            time.sleep(5)  # Send data every 5 seconds

def receive_commands():
    """Listen for movement commands and execute them."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((LUNAR_IP, LUNAR_RECEIVE_PORT))
        s.listen(5)
        print("[LUNAR] Waiting for Earth commands...")

        while True:
            conn, addr = s.accept()
            print(f"[LUNAR] Connected to Earth at {addr}")
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    packet_id, packet_type, command, timestamp = LunarPacket.parse(data)

                    if packet_type == 2:
                        rover_control.execute_movement(command)  # Execute movement command
                        channel.send_w_delay_loss(conn, str(packet_id).encode())  # Send ACK

# Run telemetry and command handling in parallel
if __name__ == "__main__":
    send_thread = threading.Thread(target=send_data, daemon=True)
    recv_thread = threading.Thread(target=receive_commands, daemon=True)

    send_thread.start()
    recv_thread.start()

    send_thread.join()
    recv_thread.join()
