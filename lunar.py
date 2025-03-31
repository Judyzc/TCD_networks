import socket
import time
import random
import threading
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel
from scanner import scan_ips

# UDP instead of TCP 
UDP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_SOCKET.settimeout(1) # timeout for ACK
acknowledged_packets = set() 
lock = threading.Lock()


def send_packet(packet, address):
    """Send a LunarPacket using UDP."""

    try:
        packet_data = packet.build()
        not_lost = channel.send_w_delay_loss(UDP_SOCKET, packet_data, address, packet.packet_id)
        if not_lost:
            print(f"[LUNAR] ID={packet.packet_id} *SENT*")
        else:
            print(f"[LUNAR] Packet ID={packet.packet_id} *LOST*")
    except socket.error as e:
        print(f"[ERROR] Failed to send packet: {e}")


def send_packet_with_ack(packet, address):
    """Send a packet and wait for an ACK on the same connection (Earth just sends ACK back on same connection)."""

    send_packet(packet, address)
    start_time = time.time()
    while time.time() - start_time < 5:
        try:
            ack_data, _ = UDP_SOCKET.recvfrom(1024)  # Receive from any source
            try:
                ack_id = int(ack_data.decode().strip())
                with lock:
                    acknowledged_packets.add(ack_id)  # Store ACK
                if ack_id == packet.packet_id:
                    print(f"[LUNAR] ID={packet.packet_id} *ACK RECVD*\n")
                    return
            except (UnicodeDecodeError, ValueError) as e:
                #handle receipt of corrupted ACKs, if resend and try to get ACK
                print(f"[LUNAR] ID={packet.packet_id} *CORRUPTED ACK RECVD*")

        except socket.timeout:
            pass  # Continue waiting for ACK

    # retry?? if no ACK received -> check if needed
    print(f"[LUNAR] ID={packet.packet_id} *NO ACK* ->resend\n")
    send_packet_with_ack(packet, address)  # Resend if no ACK received


def send_temperature(packet_id, address):
    """Send temperature data packet."""

    temp_data = round(random.uniform(-150, 130), 2)  # in Celsius
    packet = LunarPacket(src_port=LUNAR_PORT, dest_port=EARTH_PORT, 
                         packet_id=packet_id, packet_type=0, data=temp_data)
    send_packet_with_ack(packet, address)


def send_system_status(packet_id, address):
    """Package lunar rover status data (battery percentage, system temperature, any errors)."""
    
    battery = round(random.uniform(10, 100), 2)  # Battery %
    sys_temp = round(random.uniform(-40, 80), 2)  # System temp in Celsius
    status_data = battery + (sys_temp / 1000) 
    packet = LunarPacket(src_port=LUNAR_PORT, dest_port=EARTH_PORT, 
                         packet_id=packet_id, packet_type=1, data=status_data) # type 1 for status
    send_packet_with_ack(packet, address)


def send_data():
    """Continuously send temperature and system status packets."""
    temp_packet_id = 0
    status_packet_id = 1000

    address = (EARTH_IP, EARTH_PORT) # just take first 

    while True:
        send_temperature(temp_packet_id, address)
        send_system_status(status_packet_id, address)
        temp_packet_id += 1
        status_packet_id += 1

        if temp_packet_id > 1000:
            temp_packet_id = 0
        if status_packet_id > 2000:  # Keep a gap 
            status_packet_id = 1000

        time.sleep(20)


if __name__ == "__main__":
    print("Lunar initialising...\n\n")
    send_data()


