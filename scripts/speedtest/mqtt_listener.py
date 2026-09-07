#!/usr/bin/env python3

import json
import logging
from datetime import datetime

import paho.mqtt.client as mqtt

from config import CONTROL_TOPIC, MQTT_BROKER, MQTT_PASSWORD, MQTT_PORT, MQTT_USERNAME

LOG_FILE = "/tmp/speedtest_mqtt_control.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)


def on_connect(client, userdata, flags, rc):
    logging.info("Connected to MQTT broker %s:%s with result code %s", MQTT_BROKER, MQTT_PORT, rc)
    client.subscribe(CONTROL_TOPIC)
    logging.info("Subscribed to %s", CONTROL_TOPIC)


def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8", errors="replace")
    logging.info("topic=%s payload=%s", message.topic, payload)


def main() -> int:
    client = mqtt.Client(client_id="speedtest_control_listener")
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        logging.info("Listener stopped by user")
        return 0
    except Exception as exc:  # pragma: no cover
        logging.exception("MQTT listener failed: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
