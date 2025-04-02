import struct
import time

class LunarPacket:
    """Class for constructing and parsing packets with UDP considerations."""
    def __init__(self, packet_id, packet_type, data):
        # 2 Bytes
        self.packet_id = packet_id 
        # 1 Byte: 0 for Temperature, 1 for System Status, 2 for ACK
        self.packet_type = packet_type  
        # 4 Bytes: actual data being sent (temperature, control, status, etc.)
        self.data = float(data)
        # 8 Bytes
        self.timestamp = int(time.time())
        
        # Total packet size is 15 bytes (2+1+4+8)
        # Well under UDP's typical MTU limit

    def build(self):
        """Create a binary representation of the packet."""
        return struct.pack('!H B f Q', self.packet_id, self.packet_type, self.data, self.timestamp)

    @staticmethod
    def parse(data):
        """Parse a received packet from binary format."""
        # Since UDP may truncate packets, check length first
        if len(data) < 15:  # 2+1+4+8 = 15 bytes
            raise ValueError("Received incomplete packet data")
            
        packet_id, packet_type, data, timestamp = struct.unpack('!H B f Q', data)
        return packet_id, packet_type, data, timestamp
    
    @staticmethod
    def parse(data):
        """Parse a received packet from binary format."""
        packet_id, packet_type, data, timestamp = struct.unpack('!H B f Q', data)
        return packet_id, packet_type, data, timestamp