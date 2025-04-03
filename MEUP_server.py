import socket
import random
import time
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel

class MEUP_server:

    def __init__(self, ip="127.0.0.1", port=5001):
        """Initialize the Receiver."""

        self.ip = ip
        self.port = port
        self.received_packets = set()
        self.UDP_SOCKET = None
        try:
            self.UDP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.UDP_SOCKET.bind((self.ip, self.port))
        except Exception as e:
            print(f"[SERVER ERROR] {e} ")
            raise
    
    def close(self):
        """Close UDP socket."""

        if self.UDP_SOCKET:
            self.UDP_SOCKET.close()
            self.UDP_SOCKET = None

    def return_ack(self, packet_id, address):
        """Return ACK for LunarPacket w/ random loss."""

        ack_message = str(packet_id).encode()
        not_dropped = channel.send_w_delay_loss(self.UDP_SOCKET, ack_message, address, packet_id)  
        if not_dropped:
            print(f"[SERVER] ID={packet_id} *ACK Sent*")
        else: 
            print(f"[SERVER] ID={packet_id} *ACK LOST*")

    # lunar to earth (telemetry)
    def parse_system_status(self, data):
        """Extract battery and system temperature from a LunarPacket."""

        battery = int(data)  # Extract integer part as battery
        sys_temp = (data - battery) * 1000 - 40  # Extract decimal part and shift back
        return battery, sys_temp

    def decode_timestamp(self, timestamp):
        """Convert Unix timestamp to human-readable format."""

        return time.strftime('%Y-%m-%d %H:%M:%S GMT', time.gmtime(timestamp))
    
    def receive_packet(self):
        """Receive Lunar Packets using UDP."""

        print("[SERVER] Listening for incoming UDP packets...\n\n")
        while True:
            if not self.UDP_SOCKET:
                print("[SERVER ERROR] Socket not initialised")
                # should it initialize ? 
                return
            try: 
                data, address = self.UDP_SOCKET.recvfrom(1024) 
                parsed_packet = LunarPacket.parse(data) 
                # parsed_packet is None if checksum error
                if parsed_packet is None:
                    print("[SERVER] ID={packet_id} *CHECKSUM INVALID* -> skipping")
                    continue 
                # Could throw error here 
                packet_id = parsed_packet["packet_id"]
                packet_type = parsed_packet["packet_type"]
                data_value = parsed_packet["data"]
                timestamp = parsed_packet["timestamp"]
                timestamp_str = self.decode_timestamp(timestamp)
                # if new packet, parse data 
                if packet_id not in self.received_packets:
                    self.received_packets.add(packet_id)
                    # PRINT ORANGE
                    # temperature
                    if packet_type == 0:
                        print(f"\n\033[38;5;214m[SERVER] ID={packet_id} *RECVD* \nTemperature: {data_value:.2f}°C., Timestamp: {timestamp_str}\033[0m")
                        # clear if over
                        if packet_id >= 1000: 
                            self.received_packets.clear()
                    # system status
                    elif packet_type == 1:
                        battery, sys_temp = self.parse_system_status(data_value)
                        print(f"\n\033[38;5;214m[SERVER] ID={packet_id} *RECVD* \nSystem Status - Battery: {battery}%, System Temp: {sys_temp:.2f}°C., Timestamp: {timestamp_str}\033[0m")
                        # clear if over 
                        if packet_id >= 2000: 
                            self.received_packets.clear()
                else: 
                    # ignore duplicate packets
                    print(f"\n[SERVER] ID={packet_id} *DUPLICATE* -> IGNORED")
                # return ACK back to client regardless of wether it was already received or not
                self.return_ack(packet_id, address)  
            except Exception as e:
                print(f"[ERROR] Failed to receive packet: {e}")

    def listen_for_data(self):
        """Start receiving packets."""

        if not self.UDP_SOCKET:
            print("[SERVER ERROR] Socket not initialized")
            return
        try:
            self.receive_packet()
        except Exception as e:
            print(f"[SERVER ERROR] {e}")
        finally:
            self.close()

    # commands
    def execute_movement(self, command):
        """Simulate executing movement commands."""

        # PRINT PURPLE
        print(f"\033[95m[ROVER] Executing Command: {command}\033[0m")
        if command == "FORWARD":
            print("\033[95m[ROVER] Moving forward...\033[0m")
            time.sleep(2)
        elif command == "BACK":
            print("\033[95m[ROVER] Moving backward...\033[0m")
            time.sleep(2)
        elif command == "LEFT":
            print("\033[95m[ROVER] Turning left...\033[0m")
            time.sleep(1)
        elif command == "RIGHT":
            print("\033[95m[ROVER] Turning right...\033[0m")
            time.sleep(1)
        elif command == "STOP":
            print("\033[95m[ROVER] Stopping...\033[0m")

    def listen_for_commands(self):
        """Handle incoming commands via UDP."""

        print(f"\033[95m[ROVER] Command server ready on UDP port {self.port}\033[0m")
        while True:
            try:
                data, addr = self.UDP_SOCKET.recvfrom(1024)
                if addr[0] != EARTH_IP:
                    continue
                cmd = data.decode().strip()
                print(f"\033[95m[ROVER] Received command: {cmd}\033[0m")
                self.execute_movement(cmd)

                # Send ACK back to Earth -> use own function ??? 
                ack_message = f"ACK {cmd}".encode()
                channel.send_w_delay_loss(self.UDP_SOCKET, ack_message, (addr[0], addr[1]), 999)
                print(f"\033[95m[ROVER] ACK Sent for {cmd}\033[0m")

            except Exception as e:
                print(f"\033[95m[ROVER] Command error: {e}\033[0m")
    
    def listen_for_scans(self): 
        """Handle incoming scan checks via UDP."""

        # PRINT YELLOW
        print(f"\033[93m[ROVER] Scanning server ready on UDP port {self.ip}:{self.port}\033[0m")
        while True:
            try:
                data, addr = self.UDP_SOCKET.recvfrom(1024)
                message = data.decode('utf-8', errors='ignore')  # Decode with error handling
                print(f"\033[93m[SERVER] Received raw data: {data} from {addr}\033[0m")  # Debug print
                
                if message == "server_check":
                    # Respond to server check scan
                    self.UDP_SOCKET.sendto(b"server_active", addr)
                    print(f"\033[93m[SERVER] Responded to scan from {addr}\033[0m")
                    
                elif message == "Would you like to share data? (y/n)":
                    # Decision to trade data - this could be based on various factors
                    # For demonstration, we'll accept trades 70% of the time
                    if random.random() < 0.7:  # 70% chance to accept
                        self.UDP_SOCKET.sendto(b"y", addr)
                        print(f"[SERVER] Accepted trade proposal from {addr}")
                        
                        # Prepare to receive data packets
                        # We'll process them in the existing packet handler
                    else:
                        self.UDP_SOCKET.sendto(b"n", addr)
                        print(f"[SERVER] Declined trade proposal from {addr}")
                
                elif len(data) == 23:  # Size of LunarPacket
                    # This might be a LunarPacket, try to parse it
                    try:
                        packet_data = LunarPacket.parse(data)
                        if packet_data and packet_data["packet_type"] == 2:  # Type 2 is for traded data
                            print(f"[SERVER] Received trade data from {addr}: {packet_data['data']}")
                            
                            # Send an ACK for the received packet
                            ack_message = str(packet_data["packet_id"]).encode()
                            self.UDP_SOCKET.sendto(ack_message, addr)
                            print(f"[SERVER] Sent ACK for packet ID {packet_data['packet_id']}")
                            
                            # Process the data as needed
                            # For example, store it, analyze it, etc.
                    except Exception as e:
                        print(f"[SERVER] Error parsing packet: {e}")
                
            except Exception as e:
                print(f"\033[93m[ROVER] Scanning error: {e}\033[0m")



