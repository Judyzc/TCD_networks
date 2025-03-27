import struct
import time

def checksum(data):
    """Compute a simple checksum."""
    return sum(data) % 65536

class LunarPacket:
    """Class for constructing and parsing packets."""
    
    def __init__(self, packet_id, packet_type, temperature):
        self.packet_id = packet_id
        self.packet_type = packet_type  # 0 = Data, 1 = ACK
        self.temperature = float(temperature)
        self.timestamp = int(time.time())

    def build(self):
        """Create a binary representation of the packet."""
        header = struct.pack('!H B f Q H', self.packet_id, self.packet_type, self.temperature, self.timestamp, 0)
        checksum_val = checksum(header)
        return struct.pack('!H B f Q H', self.packet_id, self.packet_type, self.temperature, self.timestamp, checksum_val)

    @staticmethod
    def parse(data):
        """Parse a received packet from binary format."""
        packet_id, packet_type, temperature, timestamp, received_checksum = struct.unpack('!H B f Q H', data)
        computed_checksum = checksum(data[:-2])
        is_valid = computed_checksum == received_checksum
        return packet_id, packet_type, temperature, timestamp, is_valid
