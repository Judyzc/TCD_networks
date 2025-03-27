LUNAR_IP = "x.x.x.x"  # Laptop A
EARTH_IP = "x.x.x.x"  # Laptop B
LUNAR_PORT = 5001
EARTH_PORT = 5002

MOON_TO_EARTH_LATENCY = 1.28  # seconds, one way delay
BANDWIDTH_LIMIT = 1024  # Bytes/second (simulating limited bandwidth)
PACKET_SIZE_LIMIT = 256  # Max payload size in bytes

# if UDP
MAX_RETRIES = 3 