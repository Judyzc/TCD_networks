import socket
import time
from lunar_packet import LunarPacket
from env_variables import *
import channel_simulation as channel
from MEUP_server import MEUP_server


if __name__ == "__main__":
    try:
        # UDP socket
        EarthServer = MEUP_server(EARTH_IP, EARTH_PORT)
        EarthServer.startListening()
    except Exception as e:
        print(f"[EARTH ERROR] {e} ")
    finally:
        if EarthServer:
            EarthServer.close()
        print("[EARTH] Socket closed and program exited")
