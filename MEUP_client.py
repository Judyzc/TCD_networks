import socket
import time
import random
import threading
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel

class MEUP_client:
    def __init__(self, client_ip="127.0.0.1", client_port=5000, server_ip="127.0.0.1", server_port=5001):
        """Initialize the Sender."""

        self.client_ip = client_ip
        self.client_port = client_port
        self.server_ip = server_ip
        self.server_port = server_port
        self.UDP_SOCKET = None
        self.acknowledged_packets = set()
        self.lock = threading.Lock()
        try:
            self.UDP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.UDP_SOCKET.bind((self.client_ip, self.client_port))
            # Set timeout for ACK reception
            self.UDP_SOCKET.settimeout(1)
            print(f"[CLIENT] Socket initialized on {self.client_ip}:{self.client_port}")
        except Exception as e:
            print(f"[CLIENT ERROR] Socket initialization failed: {e}")
            self.close()
            raise
            
    def close(self):
        """Close the socket connection."""

        if self.UDP_SOCKET:
            self.UDP_SOCKET.close()
            self.UDP_SOCKET = None
            print("[CLIENT] Socket closed")

    def send_packet(self, packet, address):
        """Send a LunarPacket using UDP."""

        try:
            packet_data = packet.build()
            not_lost = channel.send_w_delay_loss(self.UDP_SOCKET, packet_data, address, packet.packet_id)
            if not_lost:
                print(f"[CLIENT] ID={packet.packet_id} *SENT*")
            else:
                print(f"[CLIENT] Packet ID={packet.packet_id} *LOST*")
        except socket.error as e:
            print(f"[ERROR] Failed to send packet: {e}")


    def send_packet_with_ack(self, packet, address):
        """Send a packet and wait for an ACK on the same connection."""

        self.send_packet(packet, address)
        start_time = time.time()
        # wait for ACK with 5 second timeout
        while time.time() - start_time < 5:
            try:
                ack_data, _ = self.UDP_SOCKET.recvfrom(1024)
                try:
                    ack_id = int(ack_data.decode().strip())
                    with self.lock:
                        self.acknowledged_packets.add(ack_id)
                    if ack_id == packet.packet_id:
                        print(f"[CLIENT] ID={packet.packet_id} *ACK RECVD*\n")
                        return
                except (UnicodeDecodeError, ValueError) as e:
                    # handle receipt of corrupted ACKs, if resend and try to get ACK
                    print(f"[CLIENT] ID={packet.packet_id} *CORRUPTED ACK RECVD*")
            except socket.timeout:
                pass
        # Resend original packet if no ACK received 
        print(f"[CLIENT] ID={packet.packet_id} *NO ACK* ->resend\n")
        self.send_packet_with_ack(packet, address)


    def send_temperature(self, packet_id, address):
        """Send temperature data packet."""

        # temperature in Celsius
        temp_data = round(random.uniform(-150, 130), 2)
        packet = LunarPacket(src_port=self.client_port, dest_port=self.server_port, 
                            packet_id=packet_id, packet_type=0, data=temp_data)
        self.send_packet_with_ack(packet, address)


    def send_system_status(self, packet_id, address):
        """Package lunar rover status data (battery percentage, system temperature, any errors)."""
        
        # Battery %, system temp in Celsius 
        battery = round(random.uniform(10, 100), 2)
        sys_temp = round(random.uniform(-40, 80), 2) 
        status_data = battery + (sys_temp / 1000) 
        packet = LunarPacket(src_port=self.client_port, dest_port=self.server_port, 
                            packet_id=packet_id, packet_type=1, data=status_data)
        self.send_packet_with_ack(packet, address)


    def send_data(self):
        """Continuously send temperature and system status packets."""

        temp_packet_id = 0
        status_packet_id = 1000
        address = (self.server_ip, self.server_port)
        while True:
            self.send_temperature(temp_packet_id, address)
            self.send_system_status(status_packet_id, address)
            temp_packet_id += 1
            status_packet_id += 1
            if temp_packet_id > 1000:
                temp_packet_id = 0
            if status_packet_id > 2000:
                status_packet_id = 1000
            time.sleep(DATA_DELAY)


    def send_commands(self):
        """Send commands to Moon via UDP."""

        # Wait for Moon to initialize
        time.sleep(2)
        print(f"[EARTH] Command client ready to send to {self.server_ip}:{self.server_port}")
        while True:
            cmd = input("Command (FWD/BACK/LEFT/RIGHT/STOP): ").upper()
            if cmd in ["FWD", "BACK", "LEFT", "RIGHT", "STOP"]:
                try:
                    self.UDP_SOCKET.sendto(cmd.encode(), (self.server_ip, self.server_port))
                    print(f"[EARTH] Sent {cmd}")
                    # Wait for ACK
                    self.UDP_SOCKET.settimeout(2)
                    try:
                        ack_data, _ = self.UDP_SOCKET.recvfrom(1024)
                        ack_message = ack_data.decode()
                        if ack_message.startswith("ACK"):
                            print(f"[ACK] Received: {ack_message}")
                        else:
                            print(f"[ERROR] Unexpected ACK format: {ack_message}")
                    except socket.timeout:
                        print("[EARTH] No ACK received - command may have been lost")
                except Exception as e:
                    print(f"[ERROR] Command failed: {e}")


    def scan_ips(self, ip_list, port_list):
        """Scans a list of IPs to check if they are active on needed ports."""
    
        valid_servers = []
        for ip in ip_list:
            all_ports_active = True  
            # check necessary ports
            for port in port_list:
                try:
                    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    udp_socket.settimeout(1)
                    message = "server_check"
                    data = message.encode('utf-8')
                    udp_socket.sendto(data, (ip, port))
                    try:
                        data, _ = udp_socket.recvfrom(1024) 
                        print(f"[SCANNER] {ip}:{port} responded.")
                    except socket.timeout:
                        print(f"[SCANNER] {ip}:{port} did not respond.")
                        all_ports_active = False 
                        break
                except Exception as e:
                    print(f"[SCANNER] Error checking {ip}:{port}: {e}")
                    all_ports_active = False
                    break
                finally:
                    udp_socket.close()
            if all_ports_active:
                valid_servers.append(ip)
                print(f"[SCANNER] {ip} is a possible Server candidate (all ports responded).")

        print(f"[SCANNER] These are all possible Servers: {valid_servers}")
        return valid_servers
            