import socket
import threading
import time
from env_variables import *
import channel_simulation as channel

# Add these to env_variables.py:
SATELLITE_IP = "x.x.x.x"  # Satellite relay IP
SATELLITE_PORT = 5003      # Satellite listening port
SATELLITE_TO_LUNAR_LATENCY = 0.64  # seconds, additional one-way delay


def handle_earth_connection(earth_conn, earth_addr):
    """Handle the connection from Earth to relay to the Lunar module"""
    print(f"[SATELLITE] Connection from Earth established: {earth_addr}")
    
    try:
        # Connect to the lunar module
        lunar_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lunar_conn.connect((LUNAR_IP, LUNAR_PORT))
        print(f"[SATELLITE] Connected to Lunar module at {LUNAR_IP}:{LUNAR_PORT}")
        
        # Start threads to handle bidirectional communication
        earth_to_lunar_thread = threading.Thread(
            target=relay_data, 
            args=(earth_conn, lunar_conn, "Earth", "Lunar", SATELLITE_TO_LUNAR_LATENCY)
        )
        
        lunar_to_earth_thread = threading.Thread(
            target=relay_data, 
            args=(lunar_conn, earth_conn, "Lunar", "Earth", SATELLITE_TO_LUNAR_LATENCY)
        )
        
        earth_to_lunar_thread.daemon = True
        lunar_to_earth_thread.daemon = True
        
        earth_to_lunar_thread.start()
        lunar_to_earth_thread.start()
        
        # Wait for threads to complete
        earth_to_lunar_thread.join()
        lunar_to_earth_thread.join()
        
    except socket.error as e:
        print(f"[SATELLITE] Error connecting to Lunar module: {e}")
    finally:
        if 'lunar_conn' in locals():
            lunar_conn.close()

def relay_data(source_conn, dest_conn, source_name, dest_name, additional_latency):
    """Relay data between source and destination with simulated space delays"""
    try:
        while True:
            data = source_conn.recv(1024)
            if not data:
                print(f"[SATELLITE] {source_name} connection closed")
                break
                
            print(f"[SATELLITE] Received data from {source_name}, relaying to {dest_name}")
            
            # Add additional satellite relay latency to the normal channel delay
            def send_with_extra_delay():
                # Sleep for the additional latency caused by the satellite hop
                time.sleep(additional_latency)
                # Then use the normal channel simulation for the remaining path
                channel.send_w_delay_loss(dest_conn, data)
                
            # Create and start the thread for delayed relay
            relay_thread = threading.Thread(target=send_with_extra_delay)
            relay_thread.daemon = True
            relay_thread.start()
            
    except socket.error as e:
        print(f"[SATELLITE] Error in {source_name} to {dest_name} relay: {e}")
    finally:
        # When one direction fails, close both connections
        try:
            source_conn.close()
            dest_conn.close()
        except:
            pass

def main():
    """Main function to start the satellite relay server"""
    # Create socket for listening for Earth connections
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as satellite_server:
        satellite_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        satellite_server.bind((SATELLITE_IP, SATELLITE_PORT))
        satellite_server.listen(5)
        
        print(f"[SATELLITE] Relay started on {SATELLITE_IP}:{SATELLITE_PORT}")
        print("[SATELLITE] Waiting for Earth connections...")
        
        while True:
            try:
                earth_conn, earth_addr = satellite_server.accept()
                # Start a new thread to handle this Earth connection
                client_thread = threading.Thread(
                    target=handle_earth_connection,
                    args=(earth_conn, earth_addr)
                )
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                print(f"[SATELLITE] Error accepting connection: {e}")

if __name__ == "__main__":
    main()