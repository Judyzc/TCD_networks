# Simple TCP Satellite Relay
import socket
import threading
import time

# Configuration
SATELLITE_LISTEN_IP = "0.0.0.0"  # Listen on all interfaces
SATELLITE_PORT = 5005            # Port to listen on for Earth connections

MOON_IP = "172.20.10.3"          # IP address of the Moon server (update this)
MOON_PORT = 5005                 # Port of the Moon server

BUFFER_SIZE = 1024               # Buffer size for receiving data
RELAY_DELAY = 0.5                # Artificial delay in seconds to simulate satellite relay

def forward_message(source_socket, destination_socket, direction):
    """Forward messages from source to destination with delay"""
    try:
        while True:
            # Receive data
            data = source_socket.recv(BUFFER_SIZE)
            if not data:
                print(f"[SATELLITE] {direction} connection closed")
                break
                
            # Log the message
            print(f"[SATELLITE] Relaying {direction}: {data.decode()}")
            
            # Simulate delay
            time.sleep(RELAY_DELAY)
            
            # Forward the data
            destination_socket.sendall(data)
            
    except Exception as e:
        print(f"[SATELLITE] Error in {direction} relay: {e}")

# Create a socket to listen for Earth connections
satellite_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
satellite_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
satellite_socket.bind((SATELLITE_LISTEN_IP, SATELLITE_PORT))
satellite_socket.listen(1)

print(f"[SATELLITE] Relay listening on port {SATELLITE_PORT}")
print(f"[SATELLITE] Will relay to Moon at {MOON_IP}:{MOON_PORT}")

# Main loop
while True:
    print("[SATELLITE] Waiting for Earth connection...")
    
    # Accept connection from Earth
    earth_conn, earth_addr = satellite_socket.accept()
    print(f"[SATELLITE] Connection from Earth: {earth_addr}")
    
    try:
        # Connect to the Moon server
        moon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        moon_socket.connect((MOON_IP, MOON_PORT))
        print(f"[SATELLITE] Connected to Moon at {MOON_IP}:{MOON_PORT}")
        
        # Create and start threads for bidirectional communication
        earth_to_moon = threading.Thread(
            target=forward_message,
            args=(earth_conn, moon_socket, "Earth→Moon")
        )
        
        moon_to_earth = threading.Thread(
            target=forward_message,
            args=(moon_socket, earth_conn, "Moon→Earth")
        )
        
        earth_to_moon.daemon = True
        moon_to_earth.daemon = True
        
        earth_to_moon.start()
        moon_to_earth.start()
        
        # Wait for threads to finish
        earth_to_moon.join()
        moon_to_earth.join()
        
    except Exception as e:
        print(f"[SATELLITE] Error: {e}")
    
    finally:
        # Clean up
        print("[SATELLITE] Closing connections")
        earth_conn.close()
        if 'moon_socket' in locals():
            moon_socket.close()