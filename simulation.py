import subprocess
import time

if __name__ == "__main__":
    print("[SIMULATION] Starting Lunar and Earth processes...\n")

    # Start Earth receiver process
    earth_process = subprocess.Popen(["python3", "earth.py"])

    # Allow Earth to set up before Lunar starts sending
    time.sleep(2)

    # Start Lunar sender process
    lunar_process = subprocess.Popen(["python3", "lunar.py"])

    # Wait for both to finish (press CTRL+C to stop manually)
    try:
        lunar_process.wait()
        earth_process.wait()
    except KeyboardInterrupt:
        print("\n[SIMULATION] Stopping processes...")
        lunar_process.terminate()
        earth_process.terminate()
