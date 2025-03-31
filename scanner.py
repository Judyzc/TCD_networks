import subprocess

def scan_ips(ip_list):
    """Scans a list of IPs to see which ones are active."""

    active_ips = []
    for ip in ip_list:
        try: 
            result = subprocess.run(
                ["ping", "-c", "1", ip],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0: # successful ping 
                active_ips.append(ip)
                print(f"[SCANNER] Active - {ip} is online.")
            else:
                print(f"[SCANNER] {ip} did not respond.")
        except Exception as e:
            print(f"[SCANNER] Failed to ping {ip}: {e}")
    return active_ips
