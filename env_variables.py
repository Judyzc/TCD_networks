LUNAR_IP = "0.0.0.0"  # Laptop A
EARTH_IP = "127.0.0.1"  # Laptop B

EARTH_RECEIVE_PORT = 5101    # server: Receives telemetry (temperature, status)
EARTH_COMMAND_PORT = 5102    # client: Sends movement commands to Lunar Rover
EARTH_SCANNING_PORT = 5103   # client Earth's open port for scanning for lunar IPs

LUNAR_RECEIVE_PORT = 5201    # server: Receives movement commands from Earth
LUNAR_SEND_PORT = 5202       # client: Sends telemetry data back to Earth

# lunar friend 
LUNAR_FRIEND_IP = "127.0.0.1"
LUNAR_FRIEND_SCANNING_PORT = 5005 

# lunar scanning
LUNAR_SS_PORT = 5301   # client:
LUNAR_SR_PORT = 5302   # server: 
LUNAR_IP_RANGE = ["172.20.10.9", "172.20.10.8", "172.20.10.7", "172.20.10.6", "172.20.10.4", "172.20.10.3", "172.20.10.2", "172.20.10.1"] 
LUNAR_PORT_RANGE = [LUNAR_SR_PORT]

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
DATA_DELAY = 30