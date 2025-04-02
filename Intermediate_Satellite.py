import socket
import threading
import time
from env_variables import *
import channel_simulation as channel

def forward_data(source_socket, dest_socket, dest_addr, direction):
    """Forward data between UDP endpoints with appropriate delay"""
    try:
        while True:
            # For UDP, we need to receive both data and address
            data, addr = source_socket.recvfrom(1024)
            if not data:
                print(f"[SATELLITE] {direction} no data received")
                continue
            
            print(f"[SATELLITE] Relaying {direction} data from {addr}")
            # Add additional satellite relay delay
            extra_delay = MOON_TO_SATELLITE_TO_EARTH_LATENCY
            time.sleep(extra_delay)
            
            # Then use the normal channel simulation for UDP
            channel.send_w_delay_loss(dest_socket, data, dest_addr)
            
    except Exception as e:
        print(f"[SATELLITE] Error in {direction} relay: {e}")
    finally:
        print(f"[SATELLITE] {direction} relay terminated")

def main():
    """Main function to run the satellite relay with UDP"""
    # Create UDP sockets for lunar and earth communication
    lunar_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    earth_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # For UDP, we don't "connect" in the TCP sense, but we do need to bind
        # to listen for incoming packets
        lunar_socket.bind((SATELLITE_IP, SATELLITE_LUNAR_PORT))
        earth_socket.bind((SATELLITE_IP, SATELLITE_PORT))
        
        print(f"[SATELLITE] Relay started for lunar module at {LUNAR_IP}:{LUNAR_PORT}")
        print(f"[SATELLITE] Relay started for Earth at {EARTH_IP}:{EARTH_PORT}")
        
        # Store the destination addresses
        lunar_addr = (LUNAR_IP, LUNAR_PORT)
        earth_addr = (EARTH_IP, EARTH_PORT)
        
        # Start bidirectional forwarding
        earth_to_lunar = threading.Thread(
            target=forward_data,
            args=(earth_socket, lunar_socket, lunar_addr, "Earth→Lunar")
        )
        
        lunar_to_earth = threading.Thread(
            target=forward_data,
            args=(lunar_socket, earth_socket, earth_addr, "Lunar→Earth")
        )
        
        earth_to_lunar.daemon = True
        lunar_to_earth.daemon = True
        
        earth_to_lunar.start()
        lunar_to_earth.start()
        
        # Wait for the threads to finish (they'll run until an exception occurs)
        earth_to_lunar.join()
        lunar_to_earth.join()
                
    except Exception as e:
        print(f"[SATELLITE] Error: {e}")
    finally:
        lunar_socket.close()
        earth_socket.close()
        print("[SATELLITE] Relay shutdown")

if __name__ == "__main__":
    main()