import socket
import time
import random
import threading
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel
from MEUP_client import MEUP_client

if __name__ == "__main__":
    try:
        # UDP socket
        LunarClient = MEUP_client(LUNAR_IP, LUNAR_PORT, EARTH_IP, EARTH_PORT)
        LunarClient.send_data()
    except Exception as e:
        print(f"[LUNAR ERROR] {e} ")
    finally:
        if LunarClient:
            LunarClient.close()
        print("[LUNAR] Socket closed and program exited")