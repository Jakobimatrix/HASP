#!/usr/bin/env python3

import time

from MQTT.mqtt_client import build_payload as build_sensor_payload


def get_temperature() -> float:
    return 42.0


def build_payload(device_id: str, temperature: float) -> dict:
    def validate(value) -> str:
        if not isinstance(value, (int, float)):
            return "is not a number"
        if value != value or value in (float("inf"), float("-inf")):
            return "is not finite"
        if not -100 <= value <= 100:
            return "is outside the expected range -100 to 100 °C"
        return ""

    return build_sensor_payload(
        device_id,
        ("temperature", round(temperature, 2) if isinstance(temperature, (int, float)) else temperature, validate),
    ) | {"timestamp": int(time.time())}