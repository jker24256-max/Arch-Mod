import os
import socket
import subprocess
import re
import threading

class NetworkScanner:
    def __init__(self):
        self.gateway_ip = None
        self.local_ip = None
        self.subnet = None
        self.active_hosts = []
        self.wifi_networks = []
        self.scan_in_progress = False

    def get_network_details(self) -> dict:
        """Retrieves local IP, Gateway, Subnet and active WiFi SSID details on Linux."""
        info = {
            "local_ip": "127.0.0.1",
            "gateway_ip": "127.0.0.1",
            "subnet": "127.0.0.1/24",
            "ssid": "Ethernet / Loopback",
            "signal": "100%",
            "security": "WPA3-Enterprise (Simulated)"
        }
        
        # Check active IP and gateway using command line (Linux style)
        try:
            # Get default gateway
            route_output = subprocess.check_output("ip route show", shell=True).decode()
            gateway_match = re.search(r"default via ([\d\.]+)", route_output)
            if gateway_match:
                info["gateway_ip"] = gateway_match.group(1)
                self.gateway_ip = info["gateway_ip"]
                
            # Get active IP
            ip_output = subprocess.check_output("ip -o -4 addr show scope global", shell=True).decode()
            ip_match = re.search(r"inet ([\d\.]+)/(\d+)", ip_output)
            if ip_match:
                info["local_ip"] = ip_match.group(1)
                self.local_ip = info["local_ip"]
                cidr = ip_match.group(2)
                
                # Derive subnet (simplistic approximation for /24 etc.)
                octets = info["local_ip"].split(".")
                info["subnet"] = f"{octets[0]}.{octets[1]}.{octets[2]}.0/{cidr}"
                self.subnet = info["subnet"]
        except Exception:
            # Windows or fallback socket setup
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                info["local_ip"] = s.getsockname()[0]
                self.local_ip = info["local_ip"]
                octets = info["local_ip"].split(".")
                info["subnet"] = f"{octets[0]}.{octets[1]}.{octets[2]}.0/24"
                self.subnet = info["subnet"]
                info["gateway_ip"] = f"{octets[0]}.{octets[1]}.{octets[2]}.1"
                self.gateway_ip = info["gateway_ip"]
                s.close()
            except Exception:
                pass

        # Wi-Fi details via nmcli
        try:
            wifi_output = subprocess.check_output("nmcli -t -f active,ssid,signal,security dev wifi", shell=True).decode()
            for line in wifi_output.split("\n"):
                if line.startswith("yes:"):
                    parts = line.split(":")
                    if len(parts) >= 4:
                        info["ssid"] = parts[1]
                        info["signal"] = parts[2] + "%"
                        info["security"] = parts[3] if parts[3] else "Open"
        except Exception:
            pass

        return info

    def scan_wifi(self) -> list:
        """Scan visible Wi-Fi networks using nmcli."""
        networks = []
        try:
            wifi_output = subprocess.check_output("nmcli -t -f ssid,bssid,signal,security dev wifi", shell=True).decode()
            for line in wifi_output.split("\n"):
                if not line:
                    continue
                parts = line.split(":")
                if len(parts) >= 4:
                    networks.append({
                        "ssid": parts[0] or "<Hidden>",
                        "bssid": ":".join(parts[1:7]),
                        "signal": parts[7] if len(parts) > 7 else parts[2],
                        "security": parts[8] if len(parts) > 8 else parts[3]
                    })
        except Exception:
            # Fallback mock/simulated list if no wireless interface
            networks = [
                {"ssid": "JKER_SECURE_AP", "bssid": "00:11:22:33:44:55", "signal": "98", "security": "WPA3"},
                {"ssid": "DIRECT-CO-SmartTV", "bssid": "AA:BB:CC:DD:EE:FF", "signal": "72", "security": "WPA2-PSK"},
                {"ssid": "Home-Guest-Net", "bssid": "11:22:33:44:55:66", "signal": "45", "security": "WEP"},
                {"ssid": "Public_WiFi", "bssid": "99:88:77:66:55:44", "signal": "30", "security": "None"}
            ]
        self.wifi_networks = networks
        return networks

    def scan_subnet(self, callback_func=None) -> list:
        """Scan active subnet using socket connection attempts to ports 22, 80, 443, 445 on live IPs."""
        if self.scan_in_progress:
            return self.active_hosts
            
        self.scan_in_progress = True
        self.active_hosts = []
        
        # Get active subnet boundary
        if not self.local_ip:
            self.get_network_details()
            
        octets = self.local_ip.split(".")
        base_ip = f"{octets[0]}.{octets[1]}.{octets[2]}."
        
        lock = threading.Lock()
        
        def scan_ip(ip):
            common_ports = [21, 22, 23, 80, 443, 445, 8080]
            open_ports = []
            host_name = "Unknown"
            
            # Simple check if host is alive (quick connect to port 80/22/443 or socket ping)
            is_alive = False
            for port in [80, 22, 443, 135, 445]:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.15)
                    res = s.connect_ex((ip, port))
                    if res == 0:
                        is_alive = True
                        s.close()
                        break
                    s.close()
                except Exception:
                    pass
            
            if is_alive or ip == self.local_ip:
                # Do detailed port check
                for port in common_ports:
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.15)
                        res = s.connect_ex((ip, port))
                        if res == 0:
                            open_ports.append(port)
                        s.close()
                    except Exception:
                        pass
                
                try:
                    host_name = socket.gethostbyaddr(ip)[0]
                except Exception:
                    pass
                
                host_info = {
                    "ip": ip,
                    "hostname": host_name,
                    "ports": open_ports,
                    "role": "Gateway" if ip == self.gateway_ip else ("LocalHost" if ip == self.local_ip else "Client")
                }
                with lock:
                    self.active_hosts.append(host_info)
                    if callback_func:
                        callback_func(host_info)

        threads = []
        # Scan range .1 to .254 (using a subset or optimized threading)
        # To avoid lagging, let's scan .1 (gateway), our own ip, and 10 common IP slots, or spawn thread pool.
        # Spawning 254 threads is standard in Python for small sweeps.
        for i in range(1, 255):
            t = threading.Thread(target=scan_ip, args=(base_ip + str(i),))
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join(timeout=0.2) # Fast join limits slow-responding IPs
            
        self.scan_in_progress = False
        return self.active_hosts

    def calculate_threat_score(self, networks: list, hosts: list) -> tuple:
        """Calculates security threat score from 0 (Safe) to 100 (Critical Risk) and vulnerabilities."""
        score = 10
        vulns = []
        
        # Check active Wi-Fi security
        active_net = self.get_network_details()
        security = active_net.get("security", "None").upper()
        if "WEP" in security:
            score += 30
            vulns.append("WEP Protocol Active: Highly vulnerable to key recovery attacks.")
        elif "NONE" in security or "OPEN" in security:
            score += 40
            vulns.append("Open Wi-Fi Network: Unencrypted traffic allows sniffing/mitm.")
        elif "WPA2" in security and "WPA3" not in security:
            score += 10
            vulns.append("WPA2 Active: Lacks latest SAE forward secrecy protections.")
            
        # Check open ports on scanned network
        for host in hosts:
            ports = host.get("ports", [])
            ip = host.get("ip")
            
            if 21 in ports:
                score += 15
                vulns.append(f"FTP Port open on {ip}: Credentials sent in plaintext.")
            if 23 in ports:
                score += 25
                vulns.append(f"Telnet Port open on {ip}: Extremely insecure admin shell.")
            if 80 in ports and 443 not in ports:
                score += 10
                vulns.append(f"HTTP Server without SSL on {ip}: Insecure Web GUI.")
            if 445 in ports:
                score += 15
                vulns.append(f"SMB Port open on {ip}: Risk of SambaCry or EternalBlue exploits if unpatched.")

        score = min(score, 100)
        
        rating = "SECURE"
        if score > 75:
            rating = "CRITICAL RISK"
        elif score > 45:
            rating = "MEDIUM RISK"
        elif score > 15:
            rating = "LOW RISK"
            
        return score, rating, vulns
