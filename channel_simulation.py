import threading
import time
import socket
import random
from env_variables import MOON_TO_EARTH_LATENCY, LATENCY_JITTER_FACTOR, PACKET_LOSS_PROBABILITY, PACKET_LOSS_FACTOR

def send_w_delay_loss(conn, data):
    #Send data after simulating transmission delay using a thread
            
    # Determine if packet will be lost
    actual_loss_probability =  random.uniform(-PACKET_LOSS_FACTOR, PACKET_LOSS_FACTOR) * PACKET_LOSS_PROBABILITY
    not_dropped = random.random() > actual_loss_probability
    def send_or_drop_delayed():

        if not_dropped:

            send_jitter = random.uniform(-LATENCY_JITTER_FACTOR, LATENCY_JITTER_FACTOR) * MOON_TO_EARTH_LATENCY
            total_latency = MOON_TO_EARTH_LATENCY + send_jitter
            time.sleep(total_latency)
            try:
                conn.sendall(data)
                print(f"[CHANNEL] Data sent after {MOON_TO_EARTH_LATENCY} seconds delay")
            except (socket.error, BrokenPipeError) as e:
                print(f"[ERROR] Failed to send delayed data: {e}")
        else:
            print(f"CHANNEL] Packet lost in transmission")
    
    # Start a new thread to handle the delayed sending
    # without sleeping entire program
    thread = threading.Thread(target=send_or_drop_delayed)
    thread.daemon = True  # Daemon threads exit when the main program exits
    thread.start()
    return not_dropped  # return not dropped