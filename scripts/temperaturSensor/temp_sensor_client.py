#!/usr/bin/env python3


def get_temperature() -> float:
    return 42.0


def build_payload(device_id: str, temperature: float) -> dict:
    return {
        "device_id": device_id,
        "temperature": round(temperature, 2),
        "timestamp": int(time.time()),
    }