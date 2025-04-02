import socket
import time
import random
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel

def send_packet(packet):
    # Create UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # For UDP, no connection is needed, just send to the address
    earth_addr = (EARTH_IP, EARTH_PORT)
    
    # Simulate channel delay with threading
    not_lost = channel.send_w_delay_loss(s, packet.build(), earth_addr)
    if not_lost:
        print(f"[LUNAR] Sent Packet ID={packet.packet_id}, Data={packet.data:.2f}")
    else:
        print(f"[LUNAR] LOST Packet ID={packet.packet_id}, Data={packet.data:.2f}")
    
    # No need to close the socket immediately for UDP
    return s  # Return the socket for receiving ACKs

def receive_ack(sock):
    # Already created socket is used for receiving
    print("[LUNAR] Waiting for ACK...")
    
    # Set a timeout for receiving ACK
    sock.settimeout(5.0)
    
    try:
        # For UDP, recvfrom returns both data and sender address
        data, addr = sock.recvfrom(1024)
        print(f"[LUNAR] Received ACK from {addr}: {data.decode()}")
        return True
    except socket.timeout:
        print("[LUNAR] Timeout waiting for ACK")
        return False
    finally:
        sock.close()

if __name__ == "__main__":
    # Create a single UDP socket for sending packets and receiving ACKs
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((LUNAR_IP, LUNAR_PORT))  # Bind to Lunar IP for receiving ACKs
    
    for i in range(5):  # Send 5 packets
        data = round(random.uniform(-50, 50), 2)
        packet = LunarPacket(packet_id=i, packet_type=0, data=data)
        
        # For UDP, send directly from the socket
        earth_addr = (EARTH_IP, EARTH_PORT)
        not_lost = channel.send_w_delay_loss(udp_socket, packet.build(), earth_addr)
        
        if not_lost:
            print(f"[LUNAR] Sent Packet ID={packet.packet_id}, Data={packet.data:.2f}")
        else:
            print(f"[LUNAR] LOST Packet ID={packet.packet_id}, Data={packet.data:.2f}")
        
        # Try to receive an ACK after each send
        try:
            udp_socket.settimeout(5.0)  # 5 second timeout
            data, addr = udp_socket.recvfrom(1024)
            print(f"[LUNAR] Received ACK from {addr}: {data.decode()}")
        except socket.timeout:
            print("[LUNAR] No ACK received, continuing...")
        
        time.sleep(1)
    
    # Keep listening for any remaining ACKs
    print("[LUNAR] Continuing to listen for ACKs...")
    udp_socket.settimeout(10.0)  # 10 second timeout for final ACKs
    
    try:
        while True:
            data, addr = udp_socket.recvfrom(1024)
            print(f"[LUNAR] Received late ACK from {addr}: {data.decode()}")
    except socket.timeout:
        print("[LUNAR] No more ACKs received, exiting")
    finally:
        udp_socket.close()