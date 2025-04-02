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


if __name__ == "__main__":
    threads = []
    Telemetry = None
    Commands = None
    # Scanning = None
    try:
        # UDP socket
        Telemetry = MEUP_server(EARTH_IP, EARTH_RECEIVE_PORT)
        Commands = MEUP_client(EARTH_IP, EARTH_COMMAND_PORT, LUNAR_IP, LUNAR_RECEIVE_PORT)

        # Create and start telemetry thread
        t_thread = threading.Thread(target=telemetry_thread, args=(Telemetry,), daemon=True)
        t_thread.start()
        threads.append(t_thread)
        # PRINT ORANGE
        print("\033[38;5;214m[EARTH] Telemetry thread started\033[0m")

        # Create and start the command thread
        c_thread = threading.Thread(target=command_thread, args=(Commands,), daemon=True)
        c_thread.start()
        threads.append(c_thread)
        # PRINT PURPLE
        print("\033[95m[EARTH] Command thread started\033[0m")
        
        # Keep the main thread alive to allow all threads to run
        while True:
            time.sleep(0.1)

    except Exception as e:
        print(f"[EARTH ERROR] {e} ")

   


