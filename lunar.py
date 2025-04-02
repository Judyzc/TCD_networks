import time
import threading
from env_variables import *
from MEUP_client import MEUP_client
from MEUP_server import MEUP_server
from utils import setup_logger, log_message

# # logs put in logs/lunar
# filepath = setup_logger("lunar")


def telemetry_thread(client: MEUP_client):
    """Thread function for running the telemetry server."""
    try:
        # uses client (sends temperature and status data to earth)
        client.send_data()
    except Exception as e:
        print(f"[LUNAR TELEMETRY THREAD ERROR] {e}")

def command_thread(server: MEUP_server):
    """Thread function for running the command client."""
    try:
        # uses server (receives commands from earth)
        server.listen_for_commands()
    except Exception as e:
        print(f"[LUNAR COMMAND THREAD ERROR] {e}")

def scanning_thread(server: MEUP_server, interval):
    """Thread function for running the scanning client."""
    try:
        # keep receiving scans
        server.listen_for_scans()
        # time.sleep(interval)
    except Exception as e:
        print(f"[LUNAR SCANNING ERROR] {e}")


if __name__ == "__main__":
    threads = []
    SendTelemetry = None
    ReceiveCommands = None
    ReceiveScans = None
    try:
        # UDP socket
        SendTelemetry = MEUP_client(LUNAR_IP, LUNAR_SEND_PORT, EARTH_IP, EARTH_RECEIVE_PORT)
        ReceiveCommands = MEUP_server(LUNAR_IP, LUNAR_RECEIVE_PORT)
        ReceiveScans = MEUP_server(LUNAR_IP, LUNAR_SCANNING_PORT)

        # Create and start scanning thread
        scan_thread = threading.Thread(target=scanning_thread, args=(ReceiveScans, 10), daemon=True) 
        scan_thread.start()
        threads.append(scan_thread)
        print("[LUNAR] Scanning thread started.")

        t_thread = threading.Thread(target=telemetry_thread, args=(SendTelemetry,), daemon=True)
        t_thread.start()
        threads.append(t_thread)
        print("[LUNAR] Telemetry thread started")
        
        # Create and start the command thread
        c_thread = threading.Thread(target=command_thread, args=(ReceiveCommands,), daemon=True)
        c_thread.start()
        threads.append(c_thread)
        print("[LUNAR] Command thread started")
        
        # Keep the main thread alive to allow both threads to run
        while True:
            time.sleep(0.1)
    except Exception as e:
        print(f"[LUNAR ERROR] {e} ")