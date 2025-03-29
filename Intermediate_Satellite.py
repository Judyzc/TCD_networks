import socket
import threading
import time
from env_variables import *
import channel_simulation as channel

def forward_data(source_conn, dest_conn, direction):
    """Forward data between connections with appropriate delay"""
    try:
        while True:
            data = source_conn.recv(1024)
            if not data:
                print(f"[SATELLITE] {direction} connection closed")
                break
            
            print(f"[SATELLITE] Relaying {direction} data")
            # Add additional satellite relay delay
            extra_delay = MOON_TO_SATELLITE_TO_EARTH_LATENCY
            time.sleep(extra_delay)
            
            # Then use the normal channel simulation
            channel.send_w_delay_loss(dest_conn, data)
            
    except Exception as e:
        print(f"[SATELLITE] Error in {direction} relay: {e}")
    finally:
        print(f"[SATELLITE] {direction} relay terminated")

def main():
    """Main function to run the satellite relay"""
    # First connect to the lunar module
    lunar_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to lunar module
        lunar_socket.connect((LUNAR_IP, LUNAR_PORT))
        print(f"[SATELLITE] Connected to lunar module at {LUNAR_IP}:{LUNAR_PORT}")
        
        # Now listen for Earth connections
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as satellite_server:
            satellite_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            satellite_server.bind((SATELLITE_IP, SATELLITE_PORT))
            satellite_server.listen(1)
            print(f"[SATELLITE] Relay started on {SATELLITE_IP}:{SATELLITE_PORT}")
            
            while True:
                print("[SATELLITE] Waiting for Earth connection...")
                earth_conn, earth_addr = satellite_server.accept()
                print(f"[SATELLITE] Earth connected from {earth_addr}")
                
                # Start bidirectional forwarding
                earth_to_lunar = threading.Thread(
                    target=forward_data,
                    args=(earth_conn, lunar_socket, "Earth→Lunar")
                )
                
                lunar_to_earth = threading.Thread(
                    target=forward_data,
                    args=(lunar_socket, earth_conn, "Lunar→Earth")
                )
                
                earth_to_lunar.daemon = True
                lunar_to_earth.daemon = True
                
                earth_to_lunar.start()
                lunar_to_earth.start()
                
                # Wait for the threads to finish
                earth_to_lunar.join()
                lunar_to_earth.join()
                
                # Close earth connection when done
                earth_conn.close()
                
    except Exception as e:
        print(f"[SATELLITE] Error: {e}")
    finally:
        lunar_socket.close()
        print("[SATELLITE] Relay shutdown")

if __name__ == "__main__":
    main()