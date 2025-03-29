import socket
import time
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel

received_packets = set()

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
