#!/usr/bin/env python3
import requests
import json

URL = "https://homeassistant.local:5000/api/ping"

payload = {
    "device_id": "948e08ac-d855-495d-bd32-6a45641d50a4"
}

response = requests.post(
    URL,
    json=payload,
    verify=False,   # self-signed cert
    timeout=5
)

print("Status code:", response.status_code)
print("Response JSON:")
print(response.json())
