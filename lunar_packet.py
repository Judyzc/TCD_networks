import struct
import time

class LunarPacket:
    """Class for constructing and parsing packets."""
    
    def __init__(self, packet_id, packet_type, data):
        self.packet_id = packet_id
        self.packet_type = packet_type  # 0 = Data, 1 = ACK
        self.data = float(data)
        self.timestamp = int(time.time())

    def build(self):
        """Create a binary representation of the packet."""
        return struct.pack('!H B f Q', self.packet_id, self.packet_type, self.data, self.timestamp)

    @staticmethod
    def parse(data):
        """Parse a received packet from binary format."""
        packet_id, packet_type, data, timestamp = struct.unpack('!H B f Q', data)
        return packet_id, packet_type, data, timestamp
