import socket
import time
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel

def receive_packet():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((EARTH_IP, EARTH_PORT))  # Bind to Earth IP
        s.listen(1)  # Listen for 1 connection (TCP)
        print("[EARTH] Waiting for connection...")

        try:
            conn, addr = s.accept() 
            with conn:
                print(f"[EARTH] Connection established with {addr}")
                while True:
                    data = conn.recv(1024)
        except socket.error as e:
                print(f"[EARTH] Connection with {e} failed")
                print("[EARTH] Connecting to intermediate satellite...")

                packet_id, packet_type, data, timestamp = LunarPacket.parse(data)
                print(f"[EARTH] Received -> ID: {packet_id}, Type: {packet_type}, Data: {data:.2f}, Timestamp: {timestamp}")
                send_ack(packet_id, conn)

def send_ack(packet_id, conn):
    ack_message = f"ACK for Packet {packet_id}"
    conn.sendall(ack_message.encode())
    # Simulate channel dealy with threading
    not_dropped = channel.send_w_delay_loss(conn, ack_message.encode())
    if not_dropped:
        print(f"[EARTH] Sent ACK for Packet {packet_id}")
    else: 
        print(f"[EARTH] LOST ACK for Packet {packet_id}")

if __name__ == "__main__":
    receive_packet()
