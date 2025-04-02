import time
import threading
from env_variables import *
from MEUP_client import MEUP_client
from MEUP_server import MEUP_server
from utils import setup_logger, log_message

# # logs put in logs/lunar
# filepath = setup_logger("lunar")

# def send_scanning_thread(client: MEUP_client, interval):
#     """Thread function for running the scanning client."""
#     try:
#         # keep scanning in a loop (other client function have loop in function)
#         while True: 
#             client.scan_ips(ip_list=LUNAR_IP_RANGE, port_list=LUNAR_PORT_RANGE)
#             time.sleep(interval)
#     except Exception as e:
#         print(f"[SEND - LUNAR SCANNING ERROR] {e}")

def receive_scanning_thread(server: MEUP_server):
    """Thread function for running the scanning client."""
    try:
        # keep receiving scans
        server.listen_for_scans()
    except Exception as e:
        print(f"[RECEIVE - LUNAR SCANNING ERROR] {e}")


if __name__ == "__main__":
    threads = []
    SendTelemetry = None
    ReceiveCommands = None
    ReceiveScans = None
    SendScans = None
    try:
        # UDP socket
        ReceiveScans = MEUP_server(LUNAR_IP, LUNAR_RECEIVE_SCANNING_PORT)
        # SendScans = MEUP_client(LUNAR_IP, LUNAR_SEND_SCANNING_PORT, LUNAR_IP, LUNAR_RECEIVE_SCANNING_PORT)

        # # Create and start scanning threads
        # scan_thread = threading.Thread(target=send_scanning_thread, args=(SendScans, 10), daemon=True) 
        # scan_thread.start()
        # threads.append(scan_thread)
        # print("[LUNAR] SEND - scanning thread started.")

        s_thread = threading.Thread(target=receive_scanning_thread, args=(ReceiveScans,), daemon=True) 
        s_thread.start()
        threads.append(s_thread)
        print("[LUNAR] RECEIVE - scanning thread started.")

        # Keep the main thread alive to allow both threads to run
        while True:
            time.sleep(0.1)
    except Exception as e:
        print(f"[LUNAR ERROR] {e} ")