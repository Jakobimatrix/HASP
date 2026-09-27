#!/usr/bin/env python3

## Device config
# Machine identifier for this sensor device. Keep it unique and stable; changing it can make Home Assistant treat the sensor as a new device
DEVICE_ID = "device123"
# The human-readable name shown for the device in Home Assistant
DEVICE_NAME = "Speedtest device123"
# A short technical prefix/name used to build MQTT state/attributes topics and the MQTT client ID: TOPIC_PREFIX/DEVICE_ID/SENSOR_NAME
SENSOR_NAME = "speedtest"
# see above: TOPIC_PREFIX/DEVICE_ID/SENSOR_NAME
TOPIC_PREFIX = "devices"

# Default state of the device -> can be set via Homeassistant topic: 
DEFAULT_ENABLED = True

# Manufacturer metadata shown in Home Assistant’s device information. It is just a label
MANUFACTURER = "Jakobimatrix"
#  Model/product metadata shown alongside the manufacturer
MODEL = "speedtest"
# A label added to the sensor’s Home Assistant attributes as
TRIGGER_SOURCE = "cronjob"

## Home Assistant server config
MQTT_BROKER = "192.168.178.106"
MQTT_PORT = 1883
MQTT_USERNAME = "mqtt_user"
MQTT_PASSWORD = "test"
MQTT_KEEPALIVE = 60
# The MQTT topic prefix Home Assistant listens to for MQTT discovery. 
# The code publishes entity configuration to topics like homeassistant/sensor/DEVICE_ID_<TOPIC>/config. see discovery_topic()
# It must match Home Assistant’s configured discovery prefix; homeassistant is the usual default.
HA_DISCOVERY_PREFIX = "homeassistant"

METRICS = {
    "download": {
        "name": f"{SENSOR_NAME}_download_{DEVICE_ID}",
        "unit": "Mbit/s",
        "value_template": "{{ value_json.download }}",
        "unique_id": f"{DEVICE_ID}_{SENSOR_NAME}_download",
    },
    "upload": {
        "name": f"{SENSOR_NAME}_upload_{DEVICE_ID}",
        "unit": "Mbit/s",
        "value_template": "{{ value_json.upload }}",
        "unique_id": f"{DEVICE_ID}_{SENSOR_NAME}_upload",
    },
    "ping": {
        "name": f"{SENSOR_NAME}_ping_{DEVICE_ID}",
        "unit": "ms",
        "value_template": "{{ value_json.ping }}",
        "unique_id": f"{DEVICE_ID}_{SENSOR_NAME}_ping",
    },
    "measurement_duration": {
        "name": f"{SENSOR_NAME}_measurement_duration_{DEVICE_ID}",
        "unit": "s",
        "value_template": "{{ value_json.measurement_duration }}",
        "unique_id": f"{DEVICE_ID}_{SENSOR_NAME}_measurement_duration",
    }
}


def discovery_topic(metric: str) -> str:
    return f"{HA_DISCOVERY_PREFIX}/sensor/{DEVICE_ID}_{metric}/config"

