import socket

def scan_ips(ip_list, port_list):
    """Scans a list of IPs to check if they are active on all given UDP ports."""
    
    possible_earth = []
    for ip in ip_list:
        all_ports_active = True  
        for port in port_list:
            try:
                udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                udp_socket.settimeout(1)  # Set a short timeout (1 sec)
                message = b"earth_check"
                udp_socket.sendto(message, (ip, port))  # Send UDP packet
                try:
                    data, _ = udp_socket.recvfrom(1024)  # Try to receive a response
                    print(f"[SCANNER] {ip}:{port} responded.")
                except socket.timeout:
                    print(f"[SCANNER] {ip}:{port} did not respond.")
                    all_ports_active = False 
                    break

            except Exception as e:
                print(f"[SCANNER] Error checking {ip}:{port}: {e}")
                all_ports_active = False
                break
            finally:
                udp_socket.close()

        if all_ports_active:
            possible_earth.append(ip)
            print(f"[SCANNER] {ip} is a possible Earth candidate (all ports responded).")

    return possible_earth
