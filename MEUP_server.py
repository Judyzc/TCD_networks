import socket
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
                    # temperature
                    if packet_type == 0:
                        print(f"\n[SERVER] ID={packet_id} *RECVD* \nTemperature: {data_value:.2f}°C., Timestamp: {timestamp_str}")
                    # system status
                    elif packet_type == 1:
                        battery, sys_temp = self.parse_system_status(data_value)
                        print(f"\n[SERVER] ID={packet_id} *RECVD* \nSystem Status - Battery: {battery}%, System Temp: {sys_temp:.2f}°C., Timestamp: {timestamp_str}")
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

    # earth to lunar (commands)
    def execute_movement(self, command):
        """Simulate executing movement commands."""

        print(f"[ROVER] Executing Command: {command}")
        if command == "FORWARD":
            print("[ROVER] Moving forward...")
            time.sleep(2)
        elif command == "BACK":
            print("[ROVER] Moving backward...")
            time.sleep(2)
        elif command == "LEFT":
            print("[ROVER] Turning left...")
            time.sleep(1)
        elif command == "RIGHT":
            print("[ROVER] Turning right...")
            time.sleep(1)
        elif command == "STOP":
            print("[ROVER] Stopping...")
        else:
            print(f"[ROVER] Unknown Command: {command}")

    def listen_for_commands(self):
        """Handle incoming commands via UDP."""

        print(f"[ROVER] Command server ready on UDP port {self.port}")
        while True:
            try:
                data, addr = self.UDP_SOCKET.recvfrom(1024)
                if addr[0] != EARTH_IP:
                    continue
                cmd = data.decode().strip()
                print(f"[ROVER] Received command: {cmd}")
                self.execute_movement(cmd)

                # Send ACK back to Earth -> use own function ??? 
                ack_message = f"ACK {cmd}".encode()
                channel.send_w_delay_loss(self.UDP_SOCKET, ack_message, (addr[0], addr[1]), 999)
                print(f"[ROVER] ACK Sent for {cmd}")

            except Exception as e:
                print(f"[ROVER] Command error: {e}")
    
    def listen_for_scans(self): 
        """Handle incoming scan checks via UDP."""

        print(f"[ROVER] Scanning server ready on UDP port {self.ip}:{self.port}")
        while True:
            try:
                data, addr = self.UDP_SOCKET.recvfrom(1024)
                print(f"[SERVER] Received raw data: {data} from {addr}")  # Debug print
                
                if data.startswith(b"server_check"):
                    self.UDP_SOCKET.sendto(b"ACK_SERVER_CHECK", addr)
                    print(f"[SERVER] Responded to scan from {addr}")
            except Exception as e:
                print(f"[ROVER] Scanning error: {e}")



