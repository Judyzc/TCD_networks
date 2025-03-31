import socket
import time
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel


#go-back-N protocol variables
received_packets = set()
expected_temp_seq_num = 0     #temperature packets (0-999)
expected_status_seq_num = 1000  # status packets (1000-1999)
last_ack_temp = -1            # Last acknowledged temperature packet
last_ack_status = 999         # Last acknowledged status packet

def send_ack(packet_id, address):
    """Return ACK for Lunar Packet to Moon w/ random loss."""

    ack_message = str(packet_id).encode()
    not_dropped = channel.send_w_delay_loss(UDP_SOCKET, ack_message, address, packet_id)  
    # actual sending is done in the channel_send_w_dalay_loss function
    if not_dropped:
        print(f"[EARTH] ID={packet_id} *ACK Sent*")
    else: 
        print(f"[EARTH] ID={packet_id} *ACK LOST*")


def parse_system_status(data):
    """Extract battery and system temperature from a LunarPacket."""

    battery = int(data)  # Extract integer part as battery
    sys_temp = (data - battery) * 1000 - 40  # Extract decimal part and shift back
    return battery, sys_temp


def decode_timestamp(timestamp):
    """Convert Unix timestamp to human-readable format."""

    return time.strftime('%Y-%m-%d %H:%M:%S GMT', time.gmtime(timestamp))


def receive_packet():
    """Receive Lunar Packets from Moon through TCP with a persistent connection."""
    
    print("[EARTH] Listening for incoming UDP packets...\n\n")
    global expected_temp_seq_num, expected_status_seq_num, last_ack_temp, last_ack_status

    while True:
        try: 
            data, address = UDP_SOCKET.recvfrom(1024) 
            parsed_packet = LunarPacket.parse(data) # MIGHT BE NONE -> with checksum

            if parsed_packet is None:
                print("[EARTH] ID={packet_id} *CHECKSUM INVALID* -> skipping")
                continue  # Checksum error, skip to next iteration

            # Could throw error here 
            packet_id = parsed_packet["packet_id"]
            packet_type = parsed_packet["packet_type"]
            data_value = parsed_packet["data"]
            timestamp = parsed_packet["timestamp"]

            timestamp_str = decode_timestamp(timestamp)

            #check if arrived in sequence
            in_seq = False
            if packet_type == 0: # Temperature
                if packet_id == expected_temp_seq_num:
                    in_seq = True
                    last_ack_temp = packet_id
                    expected_temp_seq_num = (expected_temp_seq_num + 1)%1000 #modulo 1000 as it wraps around at 1000
            elif packet_type == 1: # System
                if packet_id == expected_status_seq_num:
                    in_seq = True
                    last_ack_status = packet_id
                    expected_status_seq_num = 1000  + (expected_status_seq_num - 1000 + 1)%1000 #wraps at 2000

            if in_seq:#if packet arrived in sequence

                # check if the packet has already been received -> previous ACK was lost
                if packet_id not in received_packets:
                    received_packets.add(packet_id) #update the received packets

                    if packet_type == 0:  # Temperature
                        print(f"\n[EARTH] ID={packet_id} *RECVD* \nTemperature: {data_value:.2f}°C., Timestamp: {timestamp_str}")

                    elif packet_type == 1:  # System status
                        battery, sys_temp = parse_system_status(data_value)
                        print(f"\n[EARTH] ID={packet_id} *RECVD* \nSystem Status - Battery: {battery}%, System Temp: {sys_temp:.2f}°C., Timestamp: {timestamp_str}")
                else: 
                    print(f"\n[EARTH] ID={packet_id} *DUPLICATE* -> IGNORED")
                # Send ACK back to sender regardless of wether it was already received or not
                send_ack(packet_id, address)  
            
            else: #case where not in sequence -> go-back-N
                print(f"\n[EARTH] ID={packet_id} *OUT OF SEQUENCE* -> DISCARDED")

                if packet_type == 0:
                    if last_ack_temp >= 0: # check for validity i.e. have passed the starting position
                        send_ack(last_ack_temp, address)
                        print(f"[EARTH] ID={packet_id} *GBN_T* last={last_ack_temp} ")
                elif packet_type == 1:
                    if last_ack_status >= 1000:
                        send_ack(last_ack_status, address)
                        print(f"[EARTH] ID={packet_id} *GBN_S* last={last_ack_status} ")

            if len(received_packets) >= 2000:
                received_packets.clear()

        except Exception as e:
            print(f"[ERROR] Failed to receive packet: {e}")


if __name__ == "__main__":
    try:
        # UDP socket
        UDP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDP_SOCKET.bind((EARTH_IP, EARTH_PORT))
        receive_packet()
    except Exception as e:
        print(f"[EARTH ERROR] {e} ")
    finally:
        if 'UDP_SOCKET' in locals() and UDP_SOCKET:
            UDP_SOCKET.close()
        print("[EARTH] Socket closed and program exited")
