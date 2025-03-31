import socket
import time
import random
import threading
from rover_control import execute_movement
from env_variables import *

def telemetry_client():
    """Send regular telemetry to Earth"""
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((EARTH_IP, EARTH_RECEIVE_PORT))
                print("[MOON] Connected to Earth for telemetry")
                
                while True:
                    temp = round(random.uniform(-150, 130), 2)
                    battery = round(random.uniform(10, 100), 2)
                    msg = f"Temp:{temp}°C, Battery:{battery}%"
                    s.send(msg.encode())
                    print(f"[MOON] Sent: {msg}")
                    time.sleep(5)
        except (ConnectionRefusedError, ConnectionResetError):
            print("[MOON] Waiting for Earth telemetry server...")
            time.sleep(5)

def command_server():
    """Handle commands from Earth"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((LUNAR_IP, LUNAR_RECEIVE_PORT))
        s.listen()
        print(f"[MOON] Command server ready on port {LUNAR_RECEIVE_PORT}")
        
        conn, addr = s.accept()
        print(f"[MOON] Earth connected for commands")
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                cmd = data.decode()
                execute_movement(cmd)
                conn.send(b"ACK")

if __name__ == "__main__":
    threading.Thread(target=command_server, daemon=True).start()
    telemetry_client()