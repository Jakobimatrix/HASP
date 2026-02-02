#!/usr/bin/env python3

# Register the speedtest device with the HASP server
# Call that script once before running the testInternetSpeed.py script.
import requests
import json

import from config import URL, ID, DEVICE_NAME

payload = {
    "name": DEVICE_NAME,
    "device_id": ID,
    "definition": json.dumps({
        "uses": ["api/reportValues", "api/post/state"],
        "offers": [],
        "info": "Speedtest device reporting internet speed and response time.",
        "Device": "Server"
    })
}

response = requests.post(
    URL + "registerDevice",
    json=payload,
    verify=False,
    timeout=5
)

print("Status code:", response.status_code)
try:
    print("Response JSON:", response.json())
except ValueError:
    print("Response content is not JSON:")
    print(response.text)
