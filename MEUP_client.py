import socket
import time
import random
import threading
from lunar_packet import LunarPacket
import channel_simulation as channel

class MEUP_client:
    def __init__(self, lunar_ip="127.0.0.1", lunar_port=5000, earth_ip="127.0.0.1", earth_port=5001):
        """Initialize the Sender."""

        self.lunar_ip = lunar_ip
        self.lunar_port = lunar_port
        self.earth_ip = earth_ip
        self.earth_port = earth_port
        self.UDP_SOCKET = None
        self.acknowledged_packets = set()
        self.lock = threading.Lock()  # For thread-safe access to acknowledged_packets
        
        try:
            # Initialize UDP socket
            self.UDP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.UDP_SOCKET.bind((self.lunar_ip, self.lunar_port))
            self.UDP_SOCKET.settimeout(1)  # Set timeout for ACK reception
            print(f"[LUNAR] Socket initialized on {self.lunar_ip}:{self.lunar_port}")
        except Exception as e:
            print(f"[LUNAR ERROR] Socket initialization failed: {e}")
            self.close()
            raise
            

    def send_packet(self, packet, address):
        """Send a LunarPacket using UDP."""

        try:
            packet_data = packet.build()
            not_lost = channel.send_w_delay_loss(self.UDP_SOCKET, packet_data, address, packet.packet_id)
            if not_lost:
                print(f"[LUNAR] ID={packet.packet_id} *SENT*")
            else:
                print(f"[LUNAR] Packet ID={packet.packet_id} *LOST*")
        except socket.error as e:
            print(f"[ERROR] Failed to send packet: {e}")


    def send_packet_with_ack(self, packet, address):
        """Send a packet and wait for an ACK on the same connection (Earth just sends ACK back on same connection)."""

        self.send_packet(packet, address)
        start_time = time.time()
        while time.time() - start_time < 5:
            try:
                ack_data, _ = self.UDP_SOCKET.recvfrom(1024)  # Receive from any source
                try:
                    ack_id = int(ack_data.decode().strip())
                    with self.lock:
                        self.acknowledged_packets.add(ack_id)  # Store ACK
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
        self.send_packet_with_ack(packet, address)  # Resend if no ACK received


    def send_temperature(self, packet_id, address):
        """Send temperature data packet."""

        temp_data = round(random.uniform(-150, 130), 2)  # in Celsius
        packet = LunarPacket(src_port=self.lunar_port, dest_port=self.earth_port, 
                            packet_id=packet_id, packet_type=0, data=temp_data)
        self.send_packet_with_ack(packet, address)


    def send_system_status(self, packet_id, address):
        """Package lunar rover status data (battery percentage, system temperature, any errors)."""
        
        battery = round(random.uniform(10, 100), 2)  # Battery %
        sys_temp = round(random.uniform(-40, 80), 2)  # System temp in Celsius
        status_data = battery + (sys_temp / 1000) 
        packet = LunarPacket(src_port=self.lunar_port, dest_port=self.earth_port, 
                            packet_id=packet_id, packet_type=1, data=status_data) # type 1 for status
        self.send_packet_with_ack(packet, address)


    def send_data(self):
        """Continuously send temperature and system status packets."""
        temp_packet_id = 0
        status_packet_id = 1000
        address = (self.earth_ip, self.earth_port)

        while True:
            self.send_temperature(temp_packet_id, address)
            self.send_system_status(status_packet_id, address)
            temp_packet_id += 1
            status_packet_id += 1

            if temp_packet_id > 1000:
                temp_packet_id = 0
            if status_packet_id > 2000:  # Keep a gap 
                status_packet_id = 1000

            time.sleep(20)
    
    def close(self):
        """Close the socket connection."""
        if self.UDP_SOCKET:
            self.UDP_SOCKET.close()
            self.UDP_SOCKET = None
            print("[LUNAR] Socket closed")