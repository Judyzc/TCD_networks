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

def decode_timestamp(timestamp):
    """Convert Unix timestamp to human-readable format."""
    return time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(timestamp))


def receive_packet():
    """Receive Lunar Packets from Moon through TCP with a persistent connection."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((EARTH_IP, EARTH_PORT))
        s.listen(5)  # Allow multiple connections
        print("[EARTH] Waiting for connection...")

        while True:
            try:
                conn, addr = s.accept()
                print(f"[EARTH] Connection established with {addr}")
                with conn:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break  # Exit inner loop if connection is closed
                        packet_id, packet_type, data, timestamp = LunarPacket.parse(data)
                        timestamp_str = decode_timestamp(timestamp)

                        if packet_type == 0:  # Temperature, data is temp
                            print(f"Received Temperature: {data:.4f}°C. Packet ID: {packet_id}, Timestamp: {timestamp_str}")

                        elif packet_type == 1:  # System status
                            battery, sys_temp = parse_system_status(data)
                            print(f"Received System Status - Battery: {battery}%, System Temp: {sys_temp:.4f}°C. Packet ID: {packet_id}, Timestamp: {timestamp}")

                        # print(f"[EARTH] Received -> ID: {packet_id}, Type: {packet_type}, Data: {data:.2f}, Timestamp: {timestamp}")
                        send_ack(packet_id, conn)  # Send ACK for received packet
            except socket.error as e:
                print(f"[EARTH] connection with {e} failed")
                print("Retrying connection via satellite...")
                break
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sat_conn:
        sat_conn.bind((SATELLITE_IP, SATELLITE_PORT))
        sat_conn.listen(5)  # Allow multiple connections
        print("[EARTH] Waiting for connection...")

        sconn, sat_addr = sat_conn.accept()
        print(f"[EARTH] Connection established with satellite {sat_addr}")

        try:
            with sconn:
                while True:
                    data = sat_conn.recv(1024)
                    if not data:
                        break
                    packet_id, packet_type, data, timestamp = LunarPacket.parse(data)
                    timestamp_str = decode_timestamp(timestamp)

                    if packet_type == 0:  # Temperature, data is temp
                        print(f"[VIA SATELLITE] Received Temperature: {data:.4f}°C. Packet ID: {packet_id}, Timestamp: {timestamp_str}")
                    
                    elif packet_type == 1:  # System status
                        battery, sys_temp = parse_system_status(data)
                        print(f"[VIA SATELLITE] Received System Status - Battery: {battery}%, System Temp: {sys_temp:.4f}°C. Packet ID: {packet_id}, Timestamp: {timestamp_str}")
                    
                    send_ack(packet_id, sat_conn)
        
        except socket.error as e:
            print(f"Satellite connection {e} failed")
            print(f"No available communication channel to moon or satellite...")

if __name__ == "__main__":
    receive_packet()