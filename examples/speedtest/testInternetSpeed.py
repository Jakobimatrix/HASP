#!/usr/bin/env python3
import time
import requests
import speedtest
import json

from config import URL, ID, STATES, GLOBAL_CURRENT_STATE


def post_payload(payload: dict, endpoint):
    """Send JSON payload to server and return (status_code, response_time_ms)."""
    start = time.perf_counter()
    try:
        response = requests.post(
            URL + endpoint,
            json=payload,
            verify=False,
            timeout=5
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        if not response:
            print(f"[ERROR] No response from server api {URL}{endpoint}", payload)
            return None, elapsed_ms
        
        if response.status_code != 200:
            try:
                print(f"[ERROR] {URL}{endpoint} Server response (statemachine non-JSON):", response.json(), payload)
            except ValueError:
                print(f"[ERROR] {URL}{endpoint} Server response (statemachine non-JSON):", response.text, payload)
            
            return None, elapsed_ms

        return response.json(), elapsed_ms
        
    except Exception as e:
        print(f"[ERROR] Failed to send payload to {URL}{endpoint}: {e}, payload={payload}")
        return None, None

def run_speedtest(responsetime_ms):
    st = speedtest.Speedtest(secure=True)
    st.get_best_server()

    download_speed = st.download() / 1_000_000  # Mbit/s
    upload_speed = st.upload() / 1_000_000      # Mbit/s
    ping = st.results.ping

    payload = {
        "device_id": ID,
        "keyValues": {
            "download in Mbit/s": download_speed,
            "upload in Mbit/s": upload_speed,
            "ping": ping,
            "response_time_ms": responsetime_ms
        }
    }

    post_payload(payload, "reportValues")


def saveRequestedState(requested_state):
    if(requested_state != GLOBAL_CURRENT_STATE):
        with open("config.py", "r") as f:
            lines = f.readlines()
        with open("config.py", "w") as f:
            for line in lines:
                if line.startswith("GLOBAL_CURRENT_STATE"):
                    f.write(f"GLOBAL_CURRENT_STATE = \"{requested_state}\"\n")
                else:
                    f.write(line)

def statemachine():
    payload = {
        "device_id": ID,
        "current_state": GLOBAL_CURRENT_STATE,
        "possible_states": STATES
    }

    response_json, response_time_ms = post_payload(payload, "post/state")
    if not response_json:
        return None

    if not 'state' in response_json:
        return None

    requested_state = response_json['state']
    saveRequestedState(requested_state)
 
    if(requested_state == "paused"):
        return None
    
    return response_time_ms

def run():
    responsetime_ms = statemachine()
    if responsetime_ms is None:
        return
    run_speedtest(responsetime_ms)



if __name__ == "__main__":
    run()