LUNAR_IP = "172.20.10.2"  # Laptop A
EARTH_IP = "172.20.10.2"  # Laptop B
EARTH_RECEIVE_PORT = 5001    # Receives telemetry (temperature, status)
EARTH_COMMAND_PORT = 5002    # Sends movement commands to Lunar Rover

LUNAR_RECEIVE_PORT = 5003   # Receives movement commands from Earth
LUNAR_SEND_PORT = 5004       # Sends telemetry data back to Earth

# Channel factors
MOON_TO_EARTH_LATENCY = 1.28  # seconds, one way delay
LATENCY_JITTER_FACTOR = 0.1 # Variation in travel time 
PACKET_LOSS_PROBABILITY = 0.05
PACKET_LOSS_FACTOR = 0.1


BANDWIDTH_LIMIT = 1024  # Bytes/second (simulating limited bandwidth)
PACKET_SIZE_LIMIT = 256  # Max payload size in bytes

# if UDP
MAX_RETRIES = 3 
