LUNAR_IP = "0.0.0.0"  # Laptop A
EARTH_IP = "0.0.0.0"  # Laptop B
POSSIBLE_EARTH_IPS = ["172.20.10.2", "172.20.10.5", "172.20.10.6"]
LUNAR_PORT = 5001
EARTH_PORT = 5101

# Channel factors
MOON_TO_EARTH_LATENCY = 1.28  # seconds, one way delay
LATENCY_JITTER_FACTOR = 0.1 # Variation in travel time 
PACKET_LOSS_PROBABILITY = 0.1
PACKET_LOSS_FACTOR = 0.1
BER = 0.3

BANDWIDTH_LIMIT = 1024  # Bytes/second (simulating limited bandwidth)
PACKET_SIZE_LIMIT = 256  # Max payload size in bytes

# Protocol
MAX_RETRIES = 3 