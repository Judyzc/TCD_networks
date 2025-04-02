LUNAR_IP = "127.0.0.1"  # Laptop A
LUNAR_IP_RANGE = ["127.0.0.1"] 
EARTH_IP = "127.0.0.1"  # Laptop B

EARTH_RECEIVE_PORT = 5001    # server: Receives telemetry (temperature, status)
EARTH_COMMAND_PORT = 5002    # client: Sends movement commands to Lunar Rover
EARTH_SCANNING_PORT = 5003   # client Earth's open port for scanning for lunar IPs

LUNAR_RECEIVE_PORT = 5101    # server: Receives movement commands from Earth
LUNAR_SEND_PORT = 5102       # client: Sends telemetry data back to Earth
LUNAR_PORT_RANGE = [5101]    # servers for lunar

# Channel factors
MOON_TO_EARTH_LATENCY = 1.28  # seconds, one way delay
LATENCY_JITTER_FACTOR = 0.1 # Variation in travel time 
PACKET_LOSS_PROBABILITY = 0.1
PACKET_LOSS_FACTOR = 0.1
BER = 0.05


BANDWIDTH_LIMIT = 1024  # Bytes/second (simulating limited bandwidth)
PACKET_SIZE_LIMIT = 256  # Max payload size in bytes

# if UDP
MAX_RETRIES = 3 

# sending data 
DATA_DELAY = 20 