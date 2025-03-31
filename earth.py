import socket
import threading
import time  # Added missing import
from env_variables import *

def telemetry_server():
    """Handle incoming telemetry from Moon"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((EARTH_IP, EARTH_RECEIVE_PORT))
        s.listen()
        print(f"[EARTH] Telemetry server ready on port {EARTH_RECEIVE_PORT}")
        
        conn, addr = s.accept()
        print(f"[EARTH] Moon connected for telemetry")
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"[TELEMETRY] {data.decode()}")

def command_client():
    """Send commands to Moon"""
    time.sleep(2)  # Give Moon time to start
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((LUNAR_IP, LUNAR_RECEIVE_PORT))
        print(f"[EARTH] Connected to Moon command port {LUNAR_RECEIVE_PORT}")
        
        while True:
            cmd = input("Command (FWD/BACK/LEFT/RIGHT/STOP): ").upper()
            if cmd in ["FORWARD","BACK","LEFT","RIGHT","STOP"]:
                s.send(cmd.encode())
                print(f"[EARTH] Sent {cmd}")
                print(f"[ACK] {s.recv(1024).decode()}")

if __name__ == "__main__":
    threading.Thread(target=telemetry_server, daemon=True).start()
    command_client()