import socket
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel
import rover_control  # Movement execution


def send_ack(packet_id, conn):
    """Send ACK for received command."""
    ack_message = str(packet_id)
    channel.send_w_delay_loss(conn, ack_message.encode())

def receive_commands():
    """Listen for movement commands and execute them."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((LUNAR_IP, LUNAR_PORT))
        s.listen(5)
        print("[LUNAR] Waiting for Earth commands...")

        while True:
            conn, addr = s.accept()
            print(f"[LUNAR] Connected to Earth at {addr}")
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    packet_id, packet_type, command, timestamp = LunarPacket.parse(data)

                    if packet_type == 2:  # Movement command
                        rover_control.execute_movement(command)  # Move rover
                        send_ack(packet_id, conn)  # Send ACK after execution

if __name__ == "__main__":
    receive_commands()
