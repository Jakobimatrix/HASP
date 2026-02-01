#!/usr/bin/env python3
import requests
import json

import from config import URL, ID, DEVICE_NAME

payload = {
    "name": DEVICE_NAME,
    "device_id": ID,
    "definition": json.dumps({
        "uses": ["registerDevice", "reportValues", "state"],
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
