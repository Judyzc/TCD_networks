import struct
import time
from utils import setup_logger, log_message
filepath = setup_logger("lunar_packet")

class LunarPacket:
    """Class for constructing and parsing packets: data types into bytes."""

    def __init__(self, src_port, dest_port, packet_id, packet_type, data):
        # UDP header
        self.src_port = src_port       # 2 Bytes
        self.dest_port = dest_port     # 2 Bytes
        self.packet_len = 23           # 2 Bytes (23 for 23 Bytes in length total)
        self.checksum = 0              # 2 Bytes (placeholder, calculated later)
        # Payload (Data)
        self.packet_id = packet_id     # 2 Bytes
        self.packet_type = packet_type # 1 Byte (0=temp, 1=system, etc.)
        self.data = float(data)        # 4 Bytes
        self.timestamp = int(time.time())  # 8 Bytes

    def build(self):
        """Create a binary representation of the packet, including the UDP-like header."""
        packet_without_checksum = struct.pack('!HHHH H B f Q', 
                                              self.src_port, self.dest_port, 
                                              self.packet_len, 0,   # placeholder 0 for checksum 
                                              self.packet_id, self.packet_type, 
                                              self.data, self.timestamp)
        self.checksum = self.compute_checksum(packet_without_checksum)
        return struct.pack('!HHHH H B f Q', 
                           self.src_port, self.dest_port, 
                           self.packet_len, self.checksum,  # with computed checksum 
                           self.packet_id, self.packet_type, 
                           self.data, self.timestamp)

    def compute_checksum(self, packet_data=None):
        """Compute a simple checksum based on the packet content."""
        if packet_data is None:
            packet_data = struct.pack('!HHHH H B f Q', 
                                      self.src_port, self.dest_port, 
                                      self.packet_len, 0,  # placeholder 0 for checksum 
                                      self.packet_id, self.packet_type, 
                                      self.data, self.timestamp)
        
        return sum(packet_data) % 65536  # 2 Bytes -> biggest 16-bit number = 65536, make sure checksum fits

    @staticmethod
    def parse(data):
        """Parse a received packet from binary format."""
        unpacked_data = struct.unpack('!HHHH H B f Q', data)

        src_port = unpacked_data[0]
        dest_port = unpacked_data[1]
        packet_len = unpacked_data[2]
        checksum = unpacked_data[3]
        packet_id = unpacked_data[4]
        packet_type = unpacked_data[5]
        data = unpacked_data[6]
        timestamp = unpacked_data[7]

        # Recalculate checksum 
        packet_data = struct.pack('!HHHH H B f Q', 
                                  src_port, dest_port, 
                                  packet_len, 0,  # placeholder 0 for checksum 
                                  packet_id, packet_type, 
                                  data, timestamp)
        calculated_checksum = sum(packet_data) % 65536
        if calculated_checksum != checksum:
<<<<<<< HEAD
            print(f"[ERROR] Checksum mismatch! Expected: {calculated_checksum}, Got: {checksum}")
            log_message(filepath, f"[ERROR] Checksum mismatch! Expected: {calculated_checksum}, Got: {checksum}")
=======
            print(f"\n[ERROR] Checksum mismatch! Expected: {calculated_checksum}, Got: {checksum}")
>>>>>>> 8-merge-everything
            return None  # Return None -> exceptoin will be raised in earth.py

        return {
            "src_port": src_port,
            "dest_port": dest_port,
            "packet_len": packet_len,
            "checksum": checksum,
            "packet_id": packet_id,
            "packet_type": packet_type,
            "data": data,
            "timestamp": timestamp,
        }
