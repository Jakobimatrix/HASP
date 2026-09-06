#!/usr/bin/env python3

import json
import time

import paho.mqtt.client as mqtt

from config import (
    ACK_TOPIC,
    ATTRS_TOPIC,
    CONTROL_TOPIC,
    DEVICE_ID,
    DISCOVERY_NAME,
    DISCOVERY_TEMPLATE,
    DISCOVERY_TOPICS,
    DISCOVERY_UNIQUE_ID,
    DISCOVERY_UNIT,
    HA_DISCOVERY_PREFIX,
    MQTT_BROKER,
    MQTT_PASSWORD,
    MQTT_PORT,
    MQTT_USERNAME,
    STATE_TOPIC,
)


def build_client() -> mqtt.Client:
    client = mqtt.Client(client_id=f"speedtest_{DEVICE_ID}_{int(time.time())}")
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    return client


def publish_discovery(client: mqtt.Client) -> None:
    device = {
        "identifiers": [f"hasp_{DEVICE_ID}"],
        "name": f"HASPSpeedTest {DEVICE_ID}",
        "manufacturer": "Custom",
        "model": "speedtest-poc",
    }

    for metric in ("download", "upload", "ping"):
        payload = {
            "name": DISCOVERY_NAME[metric],
            "state_topic": STATE_TOPIC,
            "value_template": DISCOVERY_TEMPLATE[metric],
            "unit_of_measurement": DISCOVERY_UNIT[metric],
            "unique_id": DISCOVERY_UNIQUE_ID[metric],
            "json_attributes_topic": ATTRS_TOPIC,
            "device": device,
        }
        client.publish(DISCOVERY_TOPICS[metric], json.dumps(payload), retain=True)
        time.sleep(0.1)


def publish_status(client: mqtt.Client, payload: dict) -> None:
    client.publish(STATE_TOPIC, json.dumps(payload), retain=True)
    time.sleep(0.1)


def publish_attributes(client: mqtt.Client, payload: dict) -> None:
    client.publish(ATTRS_TOPIC, json.dumps(payload), retain=True)
    time.sleep(0.1)


def publish_ack(client: mqtt.Client, state: str) -> None:
    client.publish(ACK_TOPIC, json.dumps({"state": state}), retain=True)
    time.sleep(0.1)


def publish_disabled_message(client: mqtt.Client) -> None:
    client.publish(CONTROL_TOPIC, json.dumps({"enabled": False, "source": "cronjob"}), retain=True)
    time.sleep(0.1)
