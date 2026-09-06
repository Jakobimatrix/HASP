#!/usr/bin/env python3

# Register the speedtest device with the HASP server
# Call that script once before running the testInternetSpeed.py script.
import requests
import json

from config import URL, ID, DEVICE_NAME

payload = {
    "name": DEVICE_NAME,
    "device_id": ID,
    "info": "speedtest",
    "device": "cronjob server"
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
