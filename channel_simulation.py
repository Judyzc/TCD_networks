import threading
import time
import socket
import random
from env_variables import MOON_TO_EARTH_LATENCY, LATENCY_JITTER_FACTOR, PACKET_LOSS_PROBABILITY, PACKET_LOSS_FACTOR, BER

from utils import setup_logger, log_message
filepath = setup_logger("channel_simulation") # just for writing into a file


def corrupt_data(data, BER):
    """Simlutaes bitwise data corruption in channel"""
    if not data:
        return data
    
    byte_array = bytearray(data)
    length = len(byte_array)

    num_corrupted_bytes = max(1, int(length * BER)) # calculate how many bytes will be corrupted

    for i in range(num_corrupted_bytes): #for each corrupted byte
        # Select a random index
        byte_index = random.randint(0, length - 1)
        bit_index = random.randint(0, 7)
        # Select a random bit index for that byte and create
        # a bit mask to flip that bit
        byte_array[byte_index] ^= (1 << bit_index)
    
    return bytes(byte_array)



def send_w_delay_loss(udp_socket, data, target_address, packet_id):
    """Send data after simulating transmission delay using a thread."""
            
    # Determine if packet will be lost
    loss_jitter = random.uniform(-PACKET_LOSS_FACTOR, PACKET_LOSS_FACTOR) * PACKET_LOSS_PROBABILITY
    actual_loss_probability = PACKET_LOSS_PROBABILITY + loss_jitter 
    not_dropped = random.random() > actual_loss_probability

    def send_or_drop_delayed():
        # if not lost, simulate bit corruption and channel delay
        if not_dropped:
            
            corrupted = False
            send_data = data

            if random.random() < BER:
                send_data = corrupt_data(data, BER)
                corrupted = True

            send_jitter = random.uniform(-LATENCY_JITTER_FACTOR, LATENCY_JITTER_FACTOR) * MOON_TO_EARTH_LATENCY
            total_latency = MOON_TO_EARTH_LATENCY + send_jitter
            time.sleep(total_latency)
            try:
                udp_socket.sendto(send_data, target_address)
                if corrupted:
                    print(f"[CHANNEL] ID={packet_id} *CORRUPTED*   {total_latency:.2f}s")
                else:
                    print(f"[CHANNEL] ID={packet_id} *SENT*        {total_latency:.2f}s")
            except (socket.error) as e:
                print(f"[CHANNEL ERROR] Failed to send delayed data: {e}")
        else:
            print(f"[CHANNEL] ID={packet_id} *LOST*                p:{actual_loss_probability:.2f}")
    
    # Start a new thread to handle the delayed sending
    # without sleeping entire program
    thread = threading.Thread(target=send_or_drop_delayed)
    thread.daemon = True  # Daemon threads exit when the main program exits
    thread.start()
    return not_dropped  # return not dropped