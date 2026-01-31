#!/usr/bin/env python3
import subprocess
from config.config import SERVICE_NAME

try:
    subprocess.run(["systemctl", "restart", SERVICE_NAME], check=True)
    print("Server restarted successfully")
except Exception as e:
    print(f"Failed to restart server: {e}")
