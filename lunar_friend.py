import time
import threading
from env_variables import *
from MEUP_server import MEUP_server


def receive_scanning_thread(server: MEUP_server):
    """Thread function for running the scanning client."""
    try:
        # keep receiving scans
        server.listen_for_scans()
    except Exception as e:
        print(f"[RECEIVE - LUNAR SCANNING ERROR] {e}")


if __name__ == "__main__":
    threads = []
    ReceiveScans = None
    try:
        # UDP socket
        ReceiveScans = MEUP_server(LUNAR_FRIEND_IP, LUNAR_FRIEND_SCANNING_PORT)

        s_thread = threading.Thread(target=receive_scanning_thread, args=(ReceiveScans,), daemon=True) 
        s_thread.start()
        threads.append(s_thread)
        print("[LUNAR] RECEIVE - scanning thread started.")

        # Keep the main thread alive to allow both threads to run
        while True:
            time.sleep(0.1)
    except Exception as e:
        print(f"[LUNAR ERROR] {e} ")