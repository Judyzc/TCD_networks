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


    def send_packet_with_ack(self, packet, address, attempt=1):
        """Send a packet and wait for an ACK on the same connection."""

        if attempt > MAX_RETRIES:
            print(f"[CLIENT] ID={packet.packet_id} *MAX RETRIES REACHED* - ABORTING\n")
            return  

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
        print(f"[CLIENT] ID={packet.packet_id} *NO ACK* -> resend, ATTEMPT={attempt}\n")
        self.send_packet_with_ack(packet, address, attempt+1)


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
        print(f"\033[95m[EARTH] Command client ready to send to {self.server_ip}:{self.server_port}\033[0m")
        while True:
            cmd = input("\033[95mCommand (FWD/BACK/LEFT/RIGHT/STOP): \033[0m").upper()
            if cmd in ["FWD", "BACK", "LEFT", "RIGHT", "STOP"]:
                try:
                    channel.send_w_delay_loss(self.UDP_SOCKET, cmd.encode(), (self.server_ip, self.server_port), 999)
                    print(f"\033[95m[EARTH] Sent {cmd}\033[0m")
                    # Wait for ACK
                    self.UDP_SOCKET.settimeout(2)
                    try:
                        ack_data, _ = self.UDP_SOCKET.recvfrom(1024)
                        ack_message = ack_data.decode()
                        if ack_message.startswith("ACK"):
                            print(f"\033[95m[ACK] Received: {ack_message}\033[0m")
                        else:
                            print(f"\033[95m[ERROR] Unexpected ACK format: {ack_message}\033[0m")
                    except socket.timeout:
                        print("\033[95m[EARTH] No ACK received - command may have been lost\033[0m")
                except Exception as e:
                    print(f"\033[95m[ERROR] Command failed: {e}\033[0m")


    def scan_ips(self, ip_list, port_list):
        """Scan ip_list for potential data trade partners

            > Does not use channel simulation as communication is local and reliable
        """
        valid_servers = []
        traders = []
        
        # Check list of ips for potential traders on set number of ports
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
                        # PRINT YELLOW
                        print(f"\033[93m[SCANNER] {ip}:{port} responded.\033[0m")
                        valid_servers.append(ip)
                    except socket.timeout:
                        print(f"\033[93m[SCANNER] {ip}:{port} did not respond.\033[0m")
                except Exception as e:
                    print(f"\033[93m[SCANNER] Error checking {ip}:{port}: {e}\033[0m")

        # Servers that are active
        print(f"\033[93m[SCANNER] These are all possible Servers: {valid_servers}\033[0m")

        # Find out if servers want to trade
        for ip in valid_servers:
            message = "Would you like to share data? (y/n)"
            data = message.encode('utf-8')
            self.UDP_SOCKET.sendto(data, (ip, port))
            try:
                data, _ = self.UDP_SOCKET.recvfrom(1024) 
                print(f"\033[34m[SCANNER] {ip}:{port} responded.\033[0m")
                if data.decode() == "y":
                    print(f"\033[34m[SCANNER] {ip}:{port} accepted trade.\033[0m")
                    traders.append((ip, port))
                elif data.decode() == "n":
                    print(f"\033[34m[SCANNER] {ip}:{port} declined trade.\033[0m")
                # print(f"[SCANNER] {ip} is a possible Server candidate (all ports responded).")
            except socket.timeout:
                print(f"\033[34m[SCANNER] {ip}:{port} did not respond.\033[0m")

        trade_threads = []
        # Create a new thread for trading with every trade partner
        for trader_ip, trader_port in traders:
            def trade_with_partner(partner_ip, partner_port):
                try:
                    # Generate a packet ID for this trade
                    trade_packet_id = 2000
                    if trade_packet_id > 3000:
                        trade_packet_id = 2000
                    # Example data packet - random for illustrative purposes
                    trade_data = round(random.uniform(0, 100), 2)
                    
                    # Create the LunarPacket
                    packet = LunarPacket(
                        src_port=self.client_port, 
                        dest_port=partner_port, 
                        packet_id=trade_packet_id, 
                        packet_type=2,  # Using type 2 for traded data
                        data=trade_data
                    )
                    
                    # Send the packet with acknowledgment
                    partner_address = (partner_ip, partner_port)
                    print(f"\033[34m[TRADER] Sending data packet to {partner_ip}:{partner_port}\033[0m")
                    self.send_packet_with_ack(packet, partner_address)
                    print(f"\033[34m[TRADER] Completed data exchange with {partner_ip}:{partner_port}\033[0m")
                except Exception as e:
                    print(f"\033[34m[TRADER ERROR] Failed to trade with {partner_ip}:{partner_port}: {e}\033[0m")
            
            # Create and start a new thread for each trading IP
            thread = threading.Thread(
                target=trade_with_partner,
                args=(trader_ip, trader_port),
                name=f"TradeThread-{trader_ip}:{trader_port}"
            )
            thread.daemon = True  # Make thread daemon so it exits when main program exits
            thread.start()
            trade_threads.append(thread)
            print(f"\033[34m[SCANNER] Started trading thread with {trader_ip}:{trader_port}\033[0m")
        
        # Wait for all trading threads to complete before next scan cycle
        for thread in trade_threads:
            thread.join(timeout=10)  # Wait up to 10 seconds for each thread
            
        # Sleep before next scan cycle
        time.sleep(30) 



        
            