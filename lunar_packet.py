import struct
import time

class LunarPacket:
    """Class for constructing and parsing packets."""
    def __init__(self, packet_id, packet_type, data):
        self.packet_id = packet_id  # 2 Bytes
        self.packet_type = packet_type  # 1 Byte (0 = temp, 1 = system, 2 = command)
        self.data = float(data)  # 4 Bytes
        self.timestamp = int(time.time())  # 8 Bytes

    def build(self):
        """Create a binary representation of the packet."""
        return struct.pack('!H B f Q', self.packet_id, self.packet_type, self.data, self.timestamp)

    @staticmethod
    def parse(data):
        """Parse a received packet from binary format and return as a dictionary."""
        try:
            packet_id, packet_type, parsed_data, timestamp = struct.unpack('!H B f Q', data)
            return {
                "packet_id": packet_id,
                "packet_type": packet_type,
                "data": parsed_data,
                "timestamp": timestamp
            }
        except struct.error:
            print("[ERROR] Failed to unpack packet - Incorrect format")
            return None
