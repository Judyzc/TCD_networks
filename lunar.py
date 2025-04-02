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


def command_server():
    """Handle incoming commands via UDP."""
    print(f"[MOON] Command server ready on UDP port {LUNAR_RECEIVE_PORT}")
    while True:
        try:
            data, addr = COMMAND_SOCKET.recvfrom(1024)
            if addr[0] != EARTH_IP:
                continue
                
            cmd = data.decode().strip()
            print(f"[MOON] Received command: {cmd}")
            execute_movement(cmd)

            # Send ACK back to Earth
            ack_message = f"ACK-{cmd}".encode()
            COMMAND_SOCKET.sendto(ack_message, (EARTH_IP, EARTH_COMMAND_PORT))
            print(f"[MOON] ACK Sent for {cmd}")

        except Exception as e:
            print(f"[MOON] Command error: {e}")


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
