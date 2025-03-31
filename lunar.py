import socket
import time
import random
import threading
from collections import OrderedDict
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel

# UDP instead of TCP 
UDP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_SOCKET.settimeout(1) # timeout for ACK

# Threading resources
lock = threading.Lock()

# Go-Back-N protocol variables
WINDOW_SIZE = 5  # Number of packets in the send window
# Separate windows for temperature and status packets to prevent one from blocking the other
temp_base = 0       # Base sequence number for temperature window (first unacknowledged)
temp_next_seq = 0   # Next sequence number to send for temperature
status_base = 1000  # Base sequence number for status window
status_next_seq = 1000  # Next sequence number to send for status

# Track sent packets that haven't been acknowledged yet
temp_window = OrderedDict()    # OrderedDict to maintain packet order: seq_num -> (packet, time, retry_count)
status_window = OrderedDict()  # OrderedDict for status packets

# Timer for oldest unacknowledged packet
temp_timer_active = False
status_timer_active = False
TIMEOUT = MOON_TO_EARTH_LATENCY * 2  # Timeout period in seconds

def send_packet(packet, address):
    """Send a LunarPacket using UDP."""
    try:
        packet_data = packet.build()
        not_lost = channel.send_w_delay_loss(UDP_SOCKET, packet_data, address, packet.packet_id)
        if not_lost:
            print(f"[LUNAR] ID={packet.packet_id} *SENT*")
        else:
            print(f"[LUNAR] Packet ID={packet.packet_id} *LOST*")
        return not_lost
    except socket.error as e:
        print(f"[ERROR] Failed to send packet: {e}")
        return False

def ack_listener():
    """Continuously listen for ACKs and update the windows."""
    global temp_base, status_base, temp_timer_active, status_timer_active
    
    while True:
        try:
            ack_data, _ = UDP_SOCKET.recvfrom(1024)
            try:
                ack_id = int(ack_data.decode().strip())
                print(f"[LUNAR] ID={ack_id} *ACK RECVD*")
                
                with lock:
                    # Determine which window this ACK belongs to
                    if 0 <= ack_id < 1000:  # Temperature packet
                        # Cumulative ACK: remove all packets up to and including this one
                        keys_to_remove = [seq for seq in temp_window.keys() if seq <= ack_id]
                        for seq in keys_to_remove:
                            del temp_window[seq]
                        
                        # Update base
                        if keys_to_remove:
                            temp_base = (ack_id + 1) % 1000
                            
                        # Reset timer if we still have packets in flight
                        if temp_window:
                            temp_timer_active = True
                        else:
                            temp_timer_active = False
                    
                    elif 1000 <= ack_id < 2000:  # Status packet
                        # Cumulative ACK: remove all packets up to and including this one
                        keys_to_remove = [seq for seq in status_window.keys() if seq <= ack_id]
                        for seq in keys_to_remove:
                            del status_window[seq]
                        
                        # Update base
                        if keys_to_remove:
                            status_base = 1000 + ((ack_id - 1000 + 1) % 1000)
                            
                        # Reset timer if we still have packets in flight
                        if status_window:
                            status_timer_active = True
                        else:
                            status_timer_active = False
                
            except (UnicodeDecodeError, ValueError) as e:
                print(f"[LUNAR] *CORRUPTED ACK RECVD*")
        except socket.timeout:
            pass  # Continue listening
        except Exception as e:
            print(f"[LUNAR] ACK listener error: {e}")

def temp_timer_handler():
    """Handle timeouts for temperature packets. Retransmit entire window on timeout."""
    global temp_timer_active
    
    while True:
        if temp_timer_active and temp_window:
            with lock:
                # Get the oldest packet's send time
                oldest_seq = next(iter(temp_window))
                _, send_time, _ = temp_window[oldest_seq]
                
                # Check if timeout occurred
                if time.time() - send_time > TIMEOUT:
                    print(f"[LUNAR] TIMEOUT for temperature window starting at {temp_base}")
                    # Go-Back-N: Retransmit all packets in the window
                    address = (EARTH_IP, EARTH_PORT)
                    for seq, (packet, _, retry_count) in list(temp_window.items()):
                        if retry_count < MAX_RETRIES:
                            print(f"[LUNAR] RETRANSMITTING ID={packet.packet_id} (retry {retry_count+1})")
                            send_packet(packet, address)
                            # Update retry count and send time
                            temp_window[seq] = (packet, time.time(), retry_count + 1)
                        else:
                            print(f"[LUNAR] MAX RETRIES REACHED for ID={packet.packet_id}, dropping")
                            # Remove from window and adjust base if this is the base
                            if seq == temp_base:
                                temp_base = (seq + 1) % 1000
                            del temp_window[seq]
                    
                    # If window is now empty, stop the timer
                    if not temp_window:
                        temp_timer_active = False
        
        # Check every 100ms to avoid busy waiting
        time.sleep(0.1)

def status_timer_handler():
    """Handle timeouts for status packets. Retransmit entire window on timeout."""
    global status_timer_active
    
    while True:
        if status_timer_active and status_window:
            with lock:
                # Get the oldest packet's send time
                oldest_seq = next(iter(status_window))
                _, send_time, _ = status_window[oldest_seq]
                
                # Check if timeout occurred
                if time.time() - send_time > TIMEOUT:
                    print(f"[LUNAR] TIMEOUT for status window starting at {status_base}")
                    # Go-Back-N: Retransmit all packets in the window
                    address = (EARTH_IP, EARTH_PORT)
                    for seq, (packet, _, retry_count) in list(status_window.items()):
                        if retry_count < MAX_RETRIES:
                            print(f"[LUNAR] RETRANSMITTING ID={packet.packet_id} (retry {retry_count+1})")
                            send_packet(packet, address)
                            # Update retry count and send time
                            status_window[seq] = (packet, time.time(), retry_count + 1)
                        else:
                            print(f"[LUNAR] MAX RETRIES REACHED for ID={packet.packet_id}, dropping")
                            # Remove from window and adjust base if this is the base
                            if seq == status_base:
                                status_base = 1000 + ((seq - 1000 + 1) % 1000)
                            del status_window[seq]
                    
                    # If window is now empty, stop the timer
                    if not status_window:
                        status_timer_active = False
        
        # Check every 100ms to avoid busy waiting
        time.sleep(0.1)

def can_send_temp():
    """Check if we can send a new temperature packet based on window size."""
    return len(temp_window) < WINDOW_SIZE

def can_send_status():
    """Check if we can send a new status packet based on window size."""
    return len(status_window) < WINDOW_SIZE

def send_temperature(address):
    """Send temperature data packet."""
    global temp_next_seq, temp_timer_active
    
    temp_data = round(random.uniform(-150, 130), 2)  # in Celsius
    packet = LunarPacket(src_port=LUNAR_PORT, dest_port=EARTH_PORT, 
                       packet_id=temp_next_seq, packet_type=0, data=temp_data)
    
    send_success = send_packet(packet, address)
    
    with lock:
        # Add to window regardless of send success (Go-Back-N considers it sent)
        temp_window[temp_next_seq] = (packet, time.time(), 0)
        
        # Start timer if this is the first packet in window
        if not temp_timer_active:
            temp_timer_active = True
        
        # Update next sequence number
        temp_next_seq = (temp_next_seq + 1) % 1000

def send_system_status(address):
    """Package lunar rover status data (battery percentage, system temperature)."""
    global status_next_seq, status_timer_active
    
    battery = round(random.uniform(10, 100), 2)  # Battery %
    sys_temp = round(random.uniform(-40, 80), 2)  # System temp in Celsius
    status_data = battery + (sys_temp / 1000)
    packet = LunarPacket(src_port=LUNAR_PORT, dest_port=EARTH_PORT, 
                       packet_id=status_next_seq, packet_type=1, data=status_data)
    
    send_success = send_packet(packet, address)
    
    with lock:
        # Add to window regardless of send success
        status_window[status_next_seq] = (packet, time.time(), 0)
        
        # Start timer if this is the first packet in window
        if not status_timer_active:
            status_timer_active = True
        
        # Update next sequence number
        status_next_seq = 1000 + ((status_next_seq - 1000 + 1) % 1000)

def send_data():
    """Continuously send temperature and system status packets."""
    address = (EARTH_IP, EARTH_PORT)
    
    while True:
        with lock:
            can_send_t = can_send_temp()
            can_send_s = can_send_status()
        
        # Try to send packets if window allows
        if can_send_t:
            send_temperature(address)
        
        if can_send_s:
            send_system_status(address)
        
        # If both windows are full, wait a bit before checking again
        if not (can_send_t or can_send_s):
            time.sleep(0.1)
        else:
            # Small delay between sends to avoid overwhelming the channel
            time.sleep(0.01)

if __name__ == "__main__":
    print("Lunar initialising with Go-Back-N protocol...\n\n")
    
    # Start ACK listener thread
    ack_thread = threading.Thread(target=ack_listener)
    ack_thread.daemon = True
    ack_thread.start()
    
    # Start timer handler threads
    temp_timer_thread = threading.Thread(target=temp_timer_handler)
    temp_timer_thread.daemon = True
    temp_timer_thread.start()
    
    status_timer_thread = threading.Thread(target=status_timer_handler)
    status_timer_thread.daemon = True
    status_timer_thread.start()
    
    # Main thread for sending data
    send_data()