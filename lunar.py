import socket
import time
import random
import threading
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel
from MEUP_client import MEUP_client
from MEUP_server import MEUP_server

def telemetry_thread(server):
    """Thread function for running the telemetry server."""
    try:
        server.send_data()
    except Exception as e:
        print(f"[TELEMETRY THREAD ERROR] {e}")


def command_thread(client):
    """Thread function for running the command client."""
    
    try:
        client.command_server()
    except Exception as e:
        print(f"[COMMAND THREAD ERROR] {e}")

if __name__ == "__main__":
    threads = []
    SendTelemetry = None
    ReceiveCommands = None
    try:
        # UDP socket
        SendTelemetry = MEUP_client(LUNAR_IP, LUNAR_SEND_PORT, EARTH_IP, EARTH_RECEIVE_PORT)
        ReceiveCommands = MEUP_server(LUNAR_IP, LUNAR_RECEIVE_PORT)

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