import socket
import time
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel

# UDP socket
UDP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_SOCKET.bind((EARTH_IP, EARTH_PORT))


def send_ack(packet_id, address):
    """Return ACK for Lunar Packet to Moon w/ random loss."""

    ack_message = str(packet_id).encode()
    not_dropped = channel.send_w_delay_loss(UDP_SOCKET, ack_message, address)  
    # actual sending is done in the channel_send_w_dalay_loss function
    if not_dropped:
        print(f"[EARTH] Sent ACK for Packet {packet_id}")
    else: 
        print(f"[EARTH] LOST ACK for Packet {packet_id}")


def parse_system_status(data):
    """Extract battery and system temperature from a LunarPacket."""

    battery = int(data)  # Extract integer part as battery
    sys_temp = (data - battery) * 1000 - 40  # Extract decimal part and shift back
    return battery, sys_temp


def decode_timestamp(timestamp):
    """Convert Unix timestamp to human-readable format."""

    return time.strftime('%Y-%m-%d %H:%M:%S GMT', time.gmtime(timestamp))


def receive_packet():
    """Receive Lunar Packets from Moon through TCP with a persistent connection."""
    
    print("[EARTH] Listening for incoming UDP packets...")
    while True:
        try: 
            data, address = UDP_SOCKET.recvfrom(1024) 
            parsed_packet = LunarPacket.parse(data) # MIGHT BE NONE -> with checksum

            if parsed_packet is None:
                print("[ERROR] Checksum, invalid packet received, skipping...")
                continue  # Checksum error, skip to next iteration

            # Could throw error here 
            packet_id = parsed_packet["packet_id"]
            packet_type = parsed_packet["packet_type"]
            data_value = parsed_packet["data"]
            timestamp = parsed_packet["timestamp"]

            timestamp_str = decode_timestamp(timestamp)

            if packet_type == 0:  # Temperature
                print(f"Received Temperature: {data_value:.2f}°C. Packet ID: {packet_id}, Timestamp: {timestamp_str}")

            elif packet_type == 1:  # System status
                battery, sys_temp = parse_system_status(data_value)
                print(f"Received System Status - Battery: {battery}%, System Temp: {sys_temp:.2f}°C. Packet ID: {packet_id}, Timestamp: {timestamp_str}")

            send_ack(packet_id, address)  # Send ACK back to sender
        except Exception as e:
            print(f"[ERROR] Failed to receive packet: {e}")


if __name__ == "__main__":
    receive_packet()
