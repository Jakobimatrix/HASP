#!/usr/bin/env python3

DEVICE_ID = "device123"
DEVICE_NAME = "Speedtest device123"
SENSOR_NAME = "speedtest"
TOPIC_PREFIX = "devices"
TRIGGER_SOURCE = "cronjob"

MQTT_BROKER = "192.168.178.106"
MQTT_PORT = 1883
MQTT_USERNAME = "mqtt2HA"
MQTT_PASSWORD = "test"
MQTT_KEEPALIVE = 60

HA_DISCOVERY_PREFIX = "homeassistant"
DEFAULT_ENABLED = True
MANUFACTURER = "Custom"
MODEL = "speedtest"

METRICS = {
    "download": {
        "name": f"speedtest_download_{DEVICE_ID}",
        "unit": "Mbit/s",
        "value_template": "{{ value_json.download }}",
        "unique_id": f"{DEVICE_ID}_speedtest_download",
    },
    "upload": {
        "name": f"speedtest_upload_{DEVICE_ID}",
        "unit": "Mbit/s",
        "value_template": "{{ value_json.upload }}",
        "unique_id": f"{DEVICE_ID}_speedtest_upload",
    },
    "ping": {
        "name": f"speedtest_ping_{DEVICE_ID}",
        "unit": "ms",
        "value_template": "{{ value_json.ping }}",
        "unique_id": f"{DEVICE_ID}_speedtest_ping",
    },
}


def discovery_topic(metric: str) -> str:
    return f"{HA_DISCOVERY_PREFIX}/sensor/{DEVICE_ID}_{metric}/config"

