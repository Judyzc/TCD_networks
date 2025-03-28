LUNAR_IP = "x.x.x.x"  # Laptop A
EARTH_IP = "x.x.x.x"  # Laptop B
LUNAR_PORT = 5001
EARTH_PORT = 5002

# Channel factors
MOON_TO_EARTH_LATENCY = 1.28  # seconds, one way delay
LATENCY_JITTER_FACTOR = 0.1 # Variation in travel time 
PACKET_LOSS_PROBABILITY = 0.05
PACKET_LOSS_FACTOR = 0.1


BANDWIDTH_LIMIT = 1024  # Bytes/second (simulating limited bandwidth)
PACKET_SIZE_LIMIT = 256  # Max payload size in bytes

# if UDP
MAX_RETRIES = 3 