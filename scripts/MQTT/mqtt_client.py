#!/usr/bin/env python3

import json
import threading
import time
from typing import Any

import paho.mqtt.client as mqtt


def _topic(config: Any, suffix: str = "") -> str:
    topic = f"{config.TOPIC_PREFIX}/{config.DEVICE_ID}/{config.SENSOR_NAME}"
    return f"{topic}/{suffix}" if suffix else topic


def state_topic(config: Any) -> str:
    return _topic(config)


def attributes_topic(config: Any) -> str:
    return _topic(config, "attrs")


def control_topic(config: Any) -> str:
    return f"{config.TOPIC_PREFIX}/{config.DEVICE_ID}/control"


def ack_topic(config: Any) -> str:
    return f"{config.TOPIC_PREFIX}/{config.DEVICE_ID}/state/ack"


def build_client(config: Any, client_id_prefix: str | None = None) -> mqtt.Client:
    prefix = client_id_prefix or config.SENSOR_NAME
    client = mqtt.Client(client_id=f"{prefix}_{config.DEVICE_ID}_{int(time.time())}")
    if config.MQTT_USERNAME:
        client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
    client.connect(config.MQTT_BROKER, config.MQTT_PORT, config.MQTT_KEEPALIVE)
    return client


def get_enabled_state(config: Any, timeout: float = 0.5) -> bool:
    client = build_client(config)
    state = {"enabled": config.DEFAULT_ENABLED}
    received = threading.Event()

    def on_message(client_obj, userdata, message):
        try:
            value = json.loads(message.payload.decode("utf-8"))
            if isinstance(value, dict):
                state.update(value)
            elif isinstance(value, bool):
                state["enabled"] = value
        except (UnicodeDecodeError, ValueError, TypeError):
            pass
        finally:
            received.set()

    try:
        client.on_message = on_message
        client.subscribe(control_topic(config))
        client.loop_start()
        received.wait(timeout)
        return bool(state.get("enabled", config.DEFAULT_ENABLED))
    finally:
        client.loop_stop()
        client.disconnect()


def publish_discovery(client: mqtt.Client, config: Any) -> None:
    device = {
        "identifiers": [config.DEVICE_ID],
        "name": config.DEVICE_NAME,
        "manufacturer": config.MANUFACTURER,
        "model": config.MODEL,
    }

    for metric, definition in config.METRICS.items():
        payload = {
            "name": definition["name"],
            "state_topic": state_topic(config),
            "value_template": definition["value_template"],
            "unique_id": definition["unique_id"],
            "json_attributes_topic": attributes_topic(config),
            "device": device,
        }
        if definition.get("unit"):
            payload["unit_of_measurement"] = definition["unit"]
        client.publish(config.discovery_topic(metric), json.dumps(payload), retain=True)


def publish_status(client: mqtt.Client, config: Any, payload: dict) -> None:
    client.publish(state_topic(config), json.dumps(payload), retain=True)


def publish_attributes(client: mqtt.Client, config: Any, payload: dict) -> None:
    client.publish(attributes_topic(config), json.dumps(payload), retain=True)


def publish_ack(client: mqtt.Client, config: Any, state: str) -> None:
    client.publish(ack_topic(config), json.dumps({"state": state}), retain=True)


def publish_control(client: mqtt.Client, config: Any, enabled: bool, source: str) -> None:
    payload = {"enabled": bool(enabled), "source": source}
    client.publish(control_topic(config), json.dumps(payload), retain=True)

def build_attributes(source: str, device_id: str, response_time_ms: int) -> dict:
    return {
          "source": source,
          "device_id": device_id,
          "response_time_ms": round(response_time_ms, 2),
          "last_update": int(time.time()),
    }