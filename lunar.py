import socket
import time
import random
import threading
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel

# put recieving ACKs into threading as well to not have hangups 
acknowledged_packets = set()
lock = threading.Lock()

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
    """Send a packet and wait for an ACK on the same connection (Earth just sends ACK back on same connection)."""

    send_packet(packet, conn)
    start_time = time.time()
    while time.time() - start_time < 5:
        try:
            ack_data = conn.recv(1024).decode().strip()
            if ack_data.isdigit() and int(ack_data) == packet.packet_id:
                print(f"[LUNAR] ACK received for Packet ID={packet.packet_id}")
                return
        except socket.timeout:
            pass  # Continue waiting for ACK ?? does this even happen
    # retry?? if no ACK received -> check if needed
    print(f"[LUNAR] No ACK for Packet ID={packet.packet_id}, resending...")
    send_packet(packet, conn)  # Resend if no ACK received


# can have a send_packet_with_ack w/ a retry counter and limit 

# def send_packet_with_ack(packet, conn, max_retries=3):
#     """Send a packet and wait for an ACK on the same connection (Earth just sends ACK back on same connection)."""
#     send_packet(packet, conn)
#     start_time = time.time()
#     retries = 0
#     while retries < max_retries and time.time() - start_time < 5:
#         try:
#             ack_data = conn.recv(1024).decode().strip()
#             if ack_data.isdigit() and int(ack_data) == packet.packet_id:
#                 print(f"[LUNAR] ACK received for Packet ID={packet.packet_id}")
#                 return
#         except socket.timeout:
#             retries += 1
#             print(f"[LUNAR] No ACK received for Packet ID={packet.packet_id}, retrying... ({retries}/{max_retries})")
#     if retries >= max_retries:
#         print(f"[LUNAR] Max retries reached for Packet ID={packet.packet_id}, giving up.")
#     else:
#         print(f"[LUNAR] No ACK for Packet ID={packet.packet_id}, resending...")
#         send_packet(packet, conn)  # Resend if no ACK received


def send_temperature(packet_id, conn):
    """Send temperature data packet."""

    temp_data = round(random.uniform(-150, 130), 2)  # in Celsius
    packet = LunarPacket(packet_id=packet_id, packet_type=0, data=temp_data)
    send_packet_with_ack(packet, conn)


def send_system_status(packet_id, conn):
    """Package lunar rover status data (battery percentage, system temperature, any errors)."""
    
    battery = round(random.uniform(10, 100), 2)  # Battery percentage
    sys_temp = round(random.uniform(-40, 80), 2)  # System temperature in Celsius
    status_data = battery + (sys_temp / 1000)  # Encoding battery + temp into one float
    packet = LunarPacket(packet_id=packet_id, packet_type=1, data=status_data)
    send_packet_with_ack(packet, conn)


def send_data():
    """Continuously send temperature and system status packets."""
    temp_packet_id = 0
    status_packet_id = 1000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
        conn.connect((EARTH_IP, EARTH_PORT))  # make a persistent connection for all sending
        conn.settimeout(1)  #  ? set timeout for ACK reception -> might cause issues
        while True:
            send_temperature(temp_packet_id, conn)
            send_system_status(status_packet_id, conn)
            temp_packet_id += 1
            status_packet_id += 1

            if status_packet_id % 1000 == 0:  # Reset IDs ? -> could cause some problems i think lol 
                temp_packet_id = 0
                status_packet_id = 1000

            time.sleep(60)


if __name__ == "__main__":
    send_data()


