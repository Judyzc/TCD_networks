import time
import threading
from env_variables import *
from MEUP_server import MEUP_server
from MEUP_client import MEUP_client
from utils import setup_logger, log_message

# # logs put in logs/earth
# filepath = setup_logger("earth")


def telemetry_thread(server: MEUP_server):
    """Thread function for running the telemetry server."""
    try:
        # uses server (receives temperature and status data from lunar)
        server.listen_for_data()
    except Exception as e:
        print(f"[EARTH TELEMETRY THREAD ERROR] {e}")

def command_thread(client: MEUP_client):
    """Thread function for running the command client."""
    try:
        # uses client (sends commands to lunar)
        client.send_commands()
    except Exception as e:
        print(f"[EARTH COMMAND THREAD ERROR] {e}")

# def scanning_thread(client: MEUP_client, interval):
#     """Thread function for running the scanning client."""
#     try:
#         # keep scanning in a loop (other client function have loop in function)
#         while True: 
#             client.scan_ips(ip_list=LUNAR_IP_RANGE, port_list=LUNAR_PORT_RANGE)
#             time.sleep(interval)
#     except Exception as e:
#         print(f"[EARTH SCANNING ERROR] {e}")

if __name__ == "__main__":
    threads = []
    Telemetry = None
    Commands = None
    # Scanning = None
    try:
        # UDP socket
        Telemetry = MEUP_server(EARTH_IP, EARTH_RECEIVE_PORT)
        Commands = MEUP_client(EARTH_IP, EARTH_COMMAND_PORT, LUNAR_IP, LUNAR_RECEIVE_PORT)
        # Scanning = MEUP_client(EARTH_IP, EARTH_SCANNING_PORT, LUNAR_IP, LUNAR_RECEIVE_PORT)

        # Create and start scanning thread
        # scan_thread = threading.Thread(target=scanning_thread, args=(Scanning, 10), daemon=True) 
        # scan_thread.start()
        # threads.append(scan_thread)
        # print("[EARTH] Scanning thread started.")

        # Create and start telemetry thread
        t_thread = threading.Thread(target=telemetry_thread, args=(Telemetry,), daemon=True)
        t_thread.start()
        threads.append(t_thread)
        print("[EARTH] Telemetry thread started")
        
        # Create and start the command thread
        c_thread = threading.Thread(target=command_thread, args=(Commands,), daemon=True)
        c_thread.start()
        threads.append(c_thread)
        print("[EARTH] Command thread started")
        
        # Keep the main thread alive to allow all threads to run
        while True:
            time.sleep(0.1)

    except Exception as e:
        print(f"[EARTH ERROR] {e} ")

   


