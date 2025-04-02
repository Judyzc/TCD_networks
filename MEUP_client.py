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

        # receiving socket
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
                    channel.send_w_delay_loss(self.UDP_SOCKET, cmd.encode(), (self.server_ip, self.server_port), 999)
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
        valid_servers = []
        traders = []
        for ip in ip_list:
            # check necessary ports
            for port in port_list:
                time.sleep(1)
                try:
                    message = "server_check"
                    data = message.encode('utf-8')
                    self.UDP_SOCKET.sendto(data, (ip, port))
                    try:
                        data, _ = self.UDP_SOCKET.recvfrom(1024) 
                        print(f"[SCANNER] {ip}:{port} responded.")
                        valid_servers.append(ip)
                        # print(f"[SCANNER] {ip} is a possible Server candidate (all ports responded).")
                    except socket.timeout:
                        print(f"[SCANNER] {ip}:{port} did not respond.")
                except Exception as e:
                    print(f"[SCANNER] Error checking {ip}:{port}: {e}")

        print(f"[SCANNER] These are all possible Servers: {valid_servers}")

        for ip in valid_servers:
            message = "Would you like to share data? (y/n)"
            data = message.encode('utf-8')
            self.UDP_SOCKET.sendto(data, (ip, port))
            try:
                data, _ = self.UDP_SOCKET.recvfrom(1024) 
                print(f"[SCANNER] {ip}:{port} responded.")
                if data.decode() == "y":
                    print(f"[SCANNER] {ip}:{port} accepted trade.")
                    traders.append((ip, port))
                elif data.decode() == "n":
                    print(f"[SCANNER] {ip}:{port} declined trade.")
                # print(f"[SCANNER] {ip} is a possible Server candidate (all ports responded).")
            except socket.timeout:
                print(f"[SCANNER] {ip}:{port} did not respond.")

        trade_threads = []
        for trader_ip, trader_port in traders:
            def trade_with_partner(partner_ip, partner_port):
                try:
                    # Generate a unique packet ID for this trade
                    trade_packet_id = random.randint(2000, 3000)
                    # Example data packet - you may want to customize this
                    trade_data = round(random.uniform(0, 100), 2)  # Example data to share
                    
                    # Create the LunarPacket with appropriate fields
                    packet = LunarPacket(
                        src_port=self.client_port, 
                        dest_port=partner_port, 
                        packet_id=trade_packet_id, 
                        packet_type=2,  # Using type 2 for traded data
                        data=trade_data
                    )
                    
                    # Send the packet with acknowledgment
                    partner_address = (partner_ip, partner_port)
                    print(f"[TRADER] Sending data packet to {partner_ip}:{partner_port}")
                    self.send_packet_with_ack(packet, partner_address)
                    print(f"[TRADER] Completed data exchange with {partner_ip}:{partner_port}")
                except Exception as e:
                    print(f"[TRADER ERROR] Failed to trade with {partner_ip}:{partner_port}: {e}")
            
            # Create and start a new thread for each trading IP
            thread = threading.Thread(
                target=trade_with_partner,
                args=(trader_ip, trader_port),
                name=f"TradeThread-{trader_ip}:{trader_port}"
            )
            thread.daemon = True  # Make thread daemon so it exits when main program exits
            thread.start()
            trade_threads.append(thread)
            print(f"[SCANNER] Started trading thread with {trader_ip}:{trader_port}")
        
        # Wait for all trading threads to complete before next scan cycle
        for thread in trade_threads:
            thread.join(timeout=10)  # Wait up to 10 seconds for each thread
            
        # Sleep before next scan cycle
        time.sleep(10)  # Adjust the scan interval as needed



        
            