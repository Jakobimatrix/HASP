#!/usr/bin/env python3

DEVICE_ID = "temperature_device123"
DEVICE_NAME = "Temperature device123"
SENSOR_NAME = "temperature"
TOPIC_PREFIX = "devices"
TRIGGER_SOURCE = "cronjob"


MQTT_BROKER = "192.168.178.106"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60
MQTT_USERNAME = "mqtt2HA"
MQTT_PASSWORD = "test"

HA_DISCOVERY_PREFIX = "homeassistant"
DEFAULT_ENABLED = True
MANUFACTURER = "Custom"
MODEL = "temperature-sensor"

METRICS = {
    "temperature": {
        "name": f"temperature_{DEVICE_ID}",
        "unit": "°C",
        "value_template": "{{ value_json.temperature }}",
        "unique_id": f"{DEVICE_ID}_temperature",
    },
}


def discovery_topic(metric: str) -> str:
    return f"{HA_DISCOVERY_PREFIX}/sensor/{DEVICE_ID}_{metric}/config"
