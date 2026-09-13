#!/usr/bin/env python3
"""Shared MQTT helpers for sensor state, attributes, control, and discovery.

Example::

    client = build_client(config)
    publish_discovery(client, config)
    publish_status(client, config, {"temperature": 21.5})
    client.disconnect()
"""

import json
import threading
import time
from typing import Any

import paho.mqtt.client as mqtt


def _topic(config: Any, suffix: str = "") -> str:
    """Build the base sensor topic, optionally with a suffix."""
    topic = f"{config.TOPIC_PREFIX}/{config.DEVICE_ID}/{config.SENSOR_NAME}"
    return f"{topic}/{suffix}" if suffix else topic


def state_topic(config: Any) -> str:
    """Return the MQTT topic for sensor state payloads."""
    return _topic(config)


def attributes_topic(config: Any) -> str:
    """Return the MQTT topic for Home Assistant attributes."""
    return _topic(config, "attrs")


def control_topic(config: Any) -> str:
    """Return the MQTT topic used to enable or disable the sensor."""
    return f"{config.TOPIC_PREFIX}/{config.DEVICE_ID}/control"


def ack_topic(config: Any) -> str:
    """Return the MQTT topic used for execution acknowledgements."""
    return f"{config.TOPIC_PREFIX}/{config.DEVICE_ID}/state/ack"


def build_client(config: Any, client_id_prefix: str | None = None) -> mqtt.Client:
    """Create, authenticate, and connect an MQTT client from config."""
    prefix = client_id_prefix or config.SENSOR_NAME
    client = mqtt.Client(client_id=f"{prefix}_{config.DEVICE_ID}_{int(time.time())}")
    if config.MQTT_USERNAME:
        client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
    client.connect(config.MQTT_BROKER, config.MQTT_PORT, config.MQTT_KEEPALIVE)
    return client


def get_enabled_state(config: Any, timeout: float = 0.5) -> bool:
    """Read the retained control state; use the configured default if absent."""
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
    """Publish retained Home Assistant discovery entries for all configured metrics."""
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

        error_payload = {
            "name": f'{definition["name"]} error',
            "state_topic": state_topic(config),
            "value_template": f'{{{{ value_json.{metric}_error }}}}',
            "unique_id": f'{definition["unique_id"]}_error',
            "entity_category": "diagnostic",
            "device": device,
        }
        client.publish(config.discovery_topic(f"{metric}_error"), json.dumps(error_payload), retain=True)


def publish_status(client: mqtt.Client, config: Any, payload: dict) -> None:
    """Publish a retained sensor-state JSON payload."""
    client.publish(state_topic(config), json.dumps(payload), retain=True)


def publish_attributes(client: mqtt.Client, config: Any, payload: dict) -> None:
    """Publish retained metadata attached to the discovered Home Assistant sensors."""
    client.publish(attributes_topic(config), json.dumps(payload), retain=True)


def publish_ack(client: mqtt.Client, config: Any, state: str) -> None:
    """Publish a retained execution status such as ``running``."""
    client.publish(ack_topic(config), json.dumps({"state": state}), retain=True)


def publish_control(client: mqtt.Client, config: Any, enabled: bool, source: str) -> None:
    """Publish a retained enable/disable command."""
    payload = {"enabled": bool(enabled), "source": source}
    client.publish(control_topic(config), json.dumps(payload), retain=True)


def build_payload(device_id: str, *readings: tuple[str, Any, Any]) -> dict:
    """Add valid readings or ``<key>_error`` messages to a sensor payload.

    Each reading is ``(key, value, validator)``. A validator returns an empty
    string for a valid value, or an error message otherwise. ``None`` accepts
    the value without validation.

    Call this first, then pass its result to ``build_attributes`` and publish
    it with ``publish_status``. For example::

        payload = build_payload(
            "device123",
            ("temperature", 21.5, validate_temperature),
        )
        publish_status(client, config, payload)
        publish_attributes(
            client,
            config,
            build_attributes("cronjob", "device123", 120.0, payload),
        )

    A valid value produces ``{"temperature": 21.5}``. An invalid value
    produces ``{"temperature_error": "..."}`` instead. The state payload
    and attribute payload are connected in Home Assistant because discovery
    configures the same entity with ``state_topic`` and
    ``json_attributes_topic``.
    """
    payload = {"device_id": device_id}
    for key, value, validator in readings:
        error = validator(value) if validator is not None else ""
        if error:
            payload[f"{key}_error"] = str(error)
        else:
            payload[key] = value
    return payload

def build_attributes(
    source: str,
    device_id: str,
    response_time_ms: float,
    payload: dict | None = None,
) -> dict:
    """Build attributes from the payload returned by ``build_payload``.

    Pass the complete payload as the fourth argument. The function finds all
    ``*_error`` fields, summarizes them in ``sensor_error``, and adds the
    error count and timestamp. Publish the result with ``publish_attributes``
    after publishing the same payload with ``publish_status``::

        payload = build_payload("device123", ("ping", -1, validate_ping))
        publish_status(client, config, payload)
        attributes = build_attributes("cronjob", "device123", 85.0, payload)
        publish_attributes(client, config, attributes)

    Home Assistant associates both messages with one entity through the
    discovery configuration, not through a direct link between MQTT messages.
    """
    errors = {
        key: value
        for key, value in (payload or {}).items()
        if key.endswith("_error") and value
    }
    return {
        "source": source,
        "device_id": device_id,
        "response_time_ms": round(response_time_ms, 2),
        "last_update": int(time.time()),
        "sensor_error": "; ".join(f"{key}: {value}" for key, value in errors.items()),
        "sensor_error_count": len(errors),
        "sensor_error_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) if errors else "",
    }