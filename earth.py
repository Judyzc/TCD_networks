import socket
import time
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel

def send_ack(packet_id, sock, addr):
    """Return ACK for Lunar Packet to Moon w/ random loss."""

    ack_message = str(packet_id)
    # Pass the socket and the sender's address for the UDP reply
    not_dropped = channel.send_w_delay_loss(sock, ack_message.encode(), addr)
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
    return time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(timestamp))


def receive_packet():
    """Receive Lunar Packets from Moon through UDP."""
    # Create UDP socket instead of TCP
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((EARTH_IP, EARTH_PORT))
        print("[EARTH] Listening for UDP packets...")

        while True:
            try:
                # For UDP, we directly receive data without establishing a connection
                data, addr = s.recvfrom(1024)
                print(f"[EARTH] Received data from {addr}")
                
                if data:
                    packet_id, packet_type, data, timestamp = LunarPacket.parse(data)
                    timestamp_str = decode_timestamp(timestamp)

                    if packet_type == 0:  # Temperature, data is temp
                        print(f"Received Temperature: {data:.4f}°C. Packet ID: {packet_id}, Timestamp: {timestamp_str}")

                    elif packet_type == 1:  # System status
                        battery, sys_temp = parse_system_status(data)
                        print(f"Received System Status - Battery: {battery}%, System Temp: {sys_temp:.4f}°C. Packet ID: {packet_id}, Timestamp: {timestamp}")

                    # Send ACK back to the sender
                    send_ack(packet_id, s, addr)
            except socket.error as e:
                print(f"[EARTH] Error receiving data: {e}")
                print("Trying satellite connection...")
                break
    
    # Create second UDP socket for satellite communication
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sat_sock:
        sat_sock.bind((SATELLITE_IP, SATELLITE_PORT))
        print("[EARTH] Listening for UDP packets via satellite...")

        try:
            while True:
                # Receive data from satellite
                data, sat_addr = sat_sock.recvfrom(1024)
                print(f"[EARTH] Received data from satellite {sat_addr}")
                
                if data:
                    packet_id, packet_type, data, timestamp = LunarPacket.parse(data)
                    timestamp_str = decode_timestamp(timestamp)

                    if packet_type == 0:  # Temperature, data is temp
                        print(f"[VIA SATELLITE] Received Temperature: {data:.4f}°C. Packet ID: {packet_id}, Timestamp: {timestamp_str}")
                    
                    elif packet_type == 1:  # System status
                        battery, sys_temp = parse_system_status(data)
                        print(f"[VIA SATELLITE] Received System Status - Battery: {battery}%, System Temp: {sys_temp:.4f}°C. Packet ID: {packet_id}, Timestamp: {timestamp_str}")
                    
                    # Send ACK back to satellite
                    send_ack(packet_id, sat_sock, sat_addr)
        
        except socket.error as e:
            print(f"Satellite connection {e} failed")
            print(f"No available communication channel to moon or satellite...")

if __name__ == "__main__":
    receive_packet()