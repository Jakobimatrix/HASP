#!/usr/bin/env python3

DEVICE_ID = "device123"
DEVICE_NAME = "Speedtest device123"

MQTT_BROKER = "192.168.178.106"
MQTT_PORT = 1883
MQTT_USERNAME = "mqtt2HA"
MQTT_PASSWORD = "test"

HA_DISCOVERY_PREFIX = "homeassistant"

CONTROL_TOPIC = f"devices/{DEVICE_ID}/control"
STATE_TOPIC = f"devices/{DEVICE_ID}/speedtest"
ATTRS_TOPIC = f"devices/{DEVICE_ID}/speedtest/attrs"
ACK_TOPIC = f"devices/{DEVICE_ID}/state/ack"

DISCOVERY_TOPICS = {
    "download": f"{HA_DISCOVERY_PREFIX}/sensor/{DEVICE_ID}_download/config",
    "upload": f"{HA_DISCOVERY_PREFIX}/sensor/{DEVICE_ID}_upload/config",
    "ping": f"{HA_DISCOVERY_PREFIX}/sensor/{DEVICE_ID}_ping/config",
}

DISCOVERY_NAME = {
    "download": f"speedtest_download_{DEVICE_ID}",
    "upload": f"speedtest_upload_{DEVICE_ID}",
    "ping": f"speedtest_ping_{DEVICE_ID}",
}

DISCOVERY_UNIT = {
    "download": "Mbit/s",
    "upload": "Mbit/s",
    "ping": "ms",
}

DISCOVERY_TEMPLATE = {
    "download": "{{ value_json.download }}",
    "upload": "{{ value_json.upload }}",
    "ping": "{{ value_json.ping }}",
}

DISCOVERY_UNIQUE_ID = {
    "download": f"{DEVICE_ID}_speedtest_download",
    "upload": f"{DEVICE_ID}_speedtest_upload",
    "ping": f"{DEVICE_ID}_speedtest_ping",
}

DEFAULT_ENABLED = True


# Optional: this is the state a cron job can read if HA is offline.
# Keep it local and update it using the `set_state.py` helper if needed.
LOCAL_STATE_FILE = "/tmp/speedtest_enabled.json"
