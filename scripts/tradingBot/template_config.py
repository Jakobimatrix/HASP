#!/usr/bin/env python3

DB_FILE = "congress_trading.db"
URL_PAGE = "mastertrader.com/Senate"
URL_BASE = "mastertrader.com"
TABLE_CLASS = "table-congress table-politician"


SUBSCRIBERS = [
    "user1@gmail.com",
    "user2@hotmail.com",
]

# Only the admin gets error notifications
ADMIN = "admin@gmail.com"

SMTP_MAIL = "sender@whatever.com"
SMTP_MAIL_PASSWORD = "*******"


### mqtt

## Device config
# Machine identifier for this sensor device. Keep it unique and stable; changing it can make Home Assistant treat the sensor as a new device
DEVICE_ID = "device123"
# The human-readable name shown for the device in Home Assistant
DEVICE_NAME = "Trade Watcher device123"
# A short technical prefix/name used to build MQTT state/attributes topics and the MQTT client ID: TOPIC_PREFIX/DEVICE_ID/SENSOR_NAME
SENSOR_NAME = "tradewatcher"
# see above: TOPIC_PREFIX/DEVICE_ID/SENSOR_NAME
TOPIC_PREFIX = "devices"

# Default state of the device -> can be set via Homeassistant topic: 
DEFAULT_ENABLED = True

# Manufacturer metadata shown in Home Assistant’s device information. It is just a label
MANUFACTURER = "Jakobimatrix"
#  Model/product metadata shown alongside the manufacturer
MODEL = "tradewatcher"
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
    "num_trades": {
        "name": f"num_trades_{DEVICE_ID}_{SENSOR_NAME}",
        "unit": "stk",
        "value_template": "{{ value_json.num_trades }}",
        "unique_id": f"{DEVICE_ID}_{SENSOR_NAME}_num_trades",
    },
    "crawl_duration": {
        "name": f"crawl_duration_{DEVICE_ID}_{SENSOR_NAME}",
        "unit": "s",
        "value_template": "{{ value_json.crawl_duration }}",
        "unique_id": f"{DEVICE_ID}_{SENSOR_NAME}_duration",
    }
}


def discovery_topic(metric: str) -> str:
    return f"{HA_DISCOVERY_PREFIX}/sensor/{DEVICE_ID}_{metric}/config"
