import time

def execute_movement(command):
    """Simulate executing movement commands."""
    print(f"[ROVER] Executing Command: {command}")

    if command == "FORWARD":
        print("[ROVER] Moving forward...")
        time.sleep(2)
    elif command == "BACKWARD":
        print("[ROVER] Moving backward...")
        time.sleep(2)
    elif command == "LEFT":
        print("[ROVER] Turning left...")
        time.sleep(1)
    elif command == "RIGHT":
        print("[ROVER] Turning right...")
        time.sleep(1)
    elif command == "STOP":
        print("[ROVER] Stopping...")
    else:
        print(f"[ROVER] Unknown Command: {command}")
