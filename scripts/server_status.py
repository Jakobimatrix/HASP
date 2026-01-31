#!/usr/bin/env python3
import subprocess
from config.config import SERVICE_NAME

try:
    result = subprocess.run(["systemctl", "is-active", SERVICE_NAME], capture_output=True, text=True)
    status = result.stdout.strip()
    if status == "active":
        print("Server is running")
    else:
        print("Server is down")
except Exception as e:
    print(f"Error checking status: {e}")
