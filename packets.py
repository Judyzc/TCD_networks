# good resource for understanding tcp packets: 
# https://www.noction.com/blog/tcp-header
# https://www.geeksforgeeks.org/services-and-segment-structure-in-tcp/

# our created packets can be similar to TCPpackets as coded using modified checksum calculations from Scapy
# https://www.kytta.dev/blog/tcp-packets-from-scratch-in-python-3/

import socket
import struct
import time
import random
from utils import timefunc

# Simulate environmental variables
MOON_TO_EARTH_LATENCY = 1.28  # seconds, one way delay
BANDWIDTH_LIMIT = 1024  # Bytes per second (simulating limited bandwidth)
PACKET_SIZE_LIMIT = 256  # Max payload size in bytes
MAX_RETRIES = 3  # Retry mechanism for packet loss


# Simple checksum function (not real, just for simplicity)
# for actual checksum, go to 
# # https://gist.github.com/kytta/b06520e3cb458ac7264cab1c51fa33d6 
def checksum(data: bytes) -> int:
    return sum(data) % 65536

class LunarPacket:
    def __init__(self, version=1, packet_type=0, seq_num=0, payload=""):
        self.version = version # protocol version, 1 Byte
        self.packet_type = packet_type # type of packet, 1 Byte, 0 for data, 1 for ACK
        self.seq_num = seq_num # sequence number, 2 Bytes
        self.payload = payload # the actual data, EX: controls, temp readings, etc.
        self.payload_len = len(payload) # length of payload, 2 Bytes
    
    def build(self):
        header = struct.pack(
            '!BBHHH',  # Format string: version, packet_type, seq_num, payload_len, checksum
            self.version,
            self.packet_type,
            self.seq_num,
            self.payload_len,
            0  # checksum placeholder
        )
        packet = header + self.payload.encode()
        checksum_val = checksum(packet)
        packet = packet[:4] + struct.pack('H', checksum_val) + packet[6:]
        return packet

# Simulate sending a packet
def send_packet(packet: LunarPacket, destination_ip="127.0.0.1", destination_port=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(packet.build(), (destination_ip, destination_port))
        print(f"Sent packet: {packet.payload} (Seq: {packet.seq_num})")

# Simulate receiving a packet
def receive_packet(s):
    data, addr = s.recvfrom(1024)
    print(f"Received packet: {data} from {addr}")
    # If you know the structure of your packet and want to decode the payload:
    # Assuming the payload starts at byte 6 and is of length 'payload_len'
    payload_len = struct.unpack('!H', data[4:6])[0]  # Extract payload length
    payload = data[6:6+payload_len].decode('utf-8', errors='ignore')  # Decode payload
    print(f"Decoded payload: {payload} \n")
    return data


# Simulate environment and communication process
def simulate_communication():
    # Initialize socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("127.0.0.1", 5000))
        
        # Simulate sending packets from Earth to Moon
        for i in range(5):  # Send 5 packets
            packet = LunarPacket(seq_num=i, payload=f"HELLO THIS IS FROM EARTH {i}")
            send_packet(packet)

            # Simulate Moon's response after a latency delay
            time.sleep(MOON_TO_EARTH_LATENCY)

            # Simulate packet loss
            if random.random() < 0.1:  # 10% packet loss
                print("Packet lost!")
                continue

            # Receive acknowledgment (or other data)
            received_data = receive_packet(s)
            # Simulate further processing

@timefunc
def main():
    simulate_communication()

if __name__ == "__main__":
    main()