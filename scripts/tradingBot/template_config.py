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


# mqtt

DEVICE_ID = "tradewatcher_device123"
DEVICE_NAME = "Trade Watcher device123"
SENSOR_NAME = "tradewatcher"
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
MODEL = "tradewatcher-sensor"

METRICS = {
    "num_trades": {
        "name": f"num_trades_{DEVICE_ID}",
        "unit": "stk",
        "value_template": "{{ value_json.num_trades }}",
        "unique_id": f"{DEVICE_ID}_num_trades",
    },
}


def discovery_topic(metric: str) -> str:
    return f"{HA_DISCOVERY_PREFIX}/sensor/{DEVICE_ID}_{metric}/config"
