import time
import threading
from env_variables import *
from MEUP_client import MEUP_client
from MEUP_server import MEUP_server


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


def send_scanning_thread(client: MEUP_client):
    """Thread function for running the scanning client."""
    try:
        # keep scanning in a loop (other client function have loop in function)
        while True: 
            client.scan_ips(ip_list=LUNAR_IP_RANGE, port_list=LUNAR_PORT_RANGE)
    except Exception as e:
        print(f"[SEND - LUNAR SCANNING ERROR] {e}")

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
        SendTelemetry = MEUP_client(LUNAR_IP, LUNAR_SEND_PORT, EARTH_IP, EARTH_RECEIVE_PORT)
        ReceiveCommands = MEUP_server(LUNAR_IP, LUNAR_RECEIVE_PORT)
        ReceiveScans = MEUP_server(LUNAR_IP, LUNAR_SR_PORT)
        SendScans = MEUP_client(LUNAR_IP, LUNAR_SS_PORT, LUNAR_IP, LUNAR_SR_PORT)

        # Create and start scanning threads
        ss_thread = threading.Thread(target=send_scanning_thread, args=(SendScans,), daemon=True) 
        ss_thread.start()
        threads.append(ss_thread)
        # PRINT YELLOW
        print("\033[93m[LUNAR] SEND - scanning thread started.\033[0m")

        sr_thread = threading.Thread(target=receive_scanning_thread, args=(ReceiveScans,), daemon=True) 
        sr_thread.start()
        threads.append(sr_thread)
        # PRINT YELLOW
        print("\033[93m[LUNAR] RECEIVE - scanning thread started.\033[0m")

        # Create and start telemetry thread
        t_thread = threading.Thread(target=telemetry_thread, args=(SendTelemetry,), daemon=True)
        t_thread.start()
        threads.append(t_thread)
        # PRINT ORANGE
        print("\033[38;5;214m[LUNAR] Telemetry thread started\033[0m")

        # Create and start the command thread
        c_thread = threading.Thread(target=command_thread, args=(ReceiveCommands,), daemon=True)
        c_thread.start()
        threads.append(c_thread)
        # PRINT PURPLE
        print("\033[95m[LUNAR] Command thread started\033[0m")

        # Keep the main thread alive to allow both threads to run
        while True:
            time.sleep(0.1)
    except Exception as e:
        print(f"[LUNAR ERROR] {e} ")