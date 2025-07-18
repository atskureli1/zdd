import random
import struct
import os

def load_proxies(file_path):
    """Load proxies from file (IP:Port format)."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def get_random_user_agent():
    """Return a realistic SA-MP User-Agent."""
    user_agents = [
        "SAMP/0.3.7",
        "SA-MP Client/0.3.7-R2",
        "SA-MP Mobile/0.3.7"
    ]
    return random.choice(user_agents)

def generate_fake_samp_packet():
    """Generate a legit-looking SA-MP packet."""
    headers = [b"SAMP", b"PLAYER", b"JOIN", b"RCON"]
    payload = (
        random.choice(headers) +
        struct.pack("I", random.randint(0, 0xFFFF)) +
        bytes([random.randint(0, 255) for _ in range(16)]))
    return payload