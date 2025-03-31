# earth.py (UDP Version)
import socket
import threading
import time
from env_variables import *
import channel_simulation as channel
from lunar_packet import LunarPacket

# UDP Sockets
TELEMETRY_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
COMMAND_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
TELEMETRY_SOCKET.bind((EARTH_IP, EARTH_RECEIVE_PORT))
COMMAND_SOCKET.bind((EARTH_IP, EARTH_COMMAND_PORT))

received_packets = set()

def send_ack(packet_id, address):
    """Send ACK for received packet."""
    ack_message = str(packet_id).encode()
    not_dropped = channel.send_w_delay_loss(TELEMETRY_SOCKET, ack_message, address)
    if not_dropped:
        print(f"[EARTH] ID={packet_id} *ACK Sent*")
    else:
        print(f"[EARTH] ID={packet_id} *ACK LOST*")

def parse_system_status(data):
    """Extract battery and system temperature."""
    battery = int(data)
    sys_temp = (data - battery) * 1000 - 40
    return battery, sys_temp

def decode_timestamp(timestamp):
    """Convert Unix timestamp to readable format."""
    return time.strftime('%Y-%m-%d %H:%M:%S GMT', time.gmtime(timestamp))

def telemetry_server():
    """Handle incoming telemetry from Moon."""
    print(f"[EARTH] Telemetry server ready on UDP port {EARTH_RECEIVE_PORT}")
    while True:
        try:
            data, address = TELEMETRY_SOCKET.recvfrom(1024)
            parsed_packet = LunarPacket.parse(data)

            if not isinstance(parsed_packet, dict):
                print("[EARTH] *CHECKSUM INVALID OR BAD DATA FORMAT* -> skipping")
                continue

            packet_id = parsed_packet.get("packet_id")
            packet_type = parsed_packet.get("packet_type")
            data_value = parsed_packet.get("data")
            timestamp = parsed_packet.get("timestamp")

            if packet_id is None or packet_type is None:
                print("[EARTH] *MALFORMED PACKET* -> skipping")
                continue

            timestamp_str = decode_timestamp(timestamp)

            if packet_id not in received_packets:
                received_packets.add(packet_id)
                if packet_type == 0:
                    print(f"\n[EARTH] ID={packet_id} *RECVD* \nTemperature: {data_value:.2f}°C, Timestamp: {timestamp_str}")
                elif packet_type == 1:
                    battery, sys_temp = parse_system_status(data_value)
                    print(f"\n[EARTH] ID={packet_id} *RECVD* \nSystem Status - Battery: {battery}%, System Temp: {sys_temp:.2f}°C, Timestamp: {timestamp_str}")
            else:
                print(f"\n[EARTH] ID={packet_id} *DUPLICATE* -> IGNORED")

            send_ack(packet_id, address)

        except Exception as e:
            print(f"[ERROR] Telemetry error: {e}")


def command_client():
    """Send commands to Moon via UDP."""
    time.sleep(2)  # Wait for Moon to initialize
    print(f"[EARTH] Command client ready to send to {LUNAR_IP}:{LUNAR_RECEIVE_PORT}")

    while True:
        cmd = input("Command (FWD/BACK/LEFT/RIGHT/STOP): ").upper()
        if cmd in ["FWD", "BACK", "LEFT", "RIGHT", "STOP"]:
            try:
                COMMAND_SOCKET.sendto(cmd.encode(), (LUNAR_IP, LUNAR_RECEIVE_PORT))
                print(f"[EARTH] Sent {cmd}")

                # Wait for ACK
                COMMAND_SOCKET.settimeout(2)
                try:
                    ack_data, _ = COMMAND_SOCKET.recvfrom(1024)
                    ack_message = ack_data.decode()
                    if ack_message.startswith("ACK"):
                        print(f"[ACK] Received: {ack_message}")
                    else:
                        print(f"[ERROR] Unexpected ACK format: {ack_message}")

                except socket.timeout:
                    print("[EARTH] No ACK received - command may have been lost")
            except Exception as e:
                print(f"[ERROR] Command failed: {e}")


if __name__ == "__main__":
    print(f"""Earth Control System Initialized
    Telemetry IN: {EARTH_RECEIVE_PORT}
    Commands OUT: {EARTH_COMMAND_PORT} → {LUNAR_RECEIVE_PORT}
    """)
    
    # Start telemetry server in separate thread
    telemetry_thread = threading.Thread(target=telemetry_server, daemon=True)
    telemetry_thread.start()
    
    # Run command client in main thread
    command_client()