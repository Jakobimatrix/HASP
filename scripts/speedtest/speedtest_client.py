#!/usr/bin/env python3

import time

import speedtest
from MQTT.mqtt_client import build_payload as build_sensor_payload


def run_speedtest() -> tuple[float, float, float]:
    st = speedtest.Speedtest(secure=True)
    st.get_best_server()
    download = st.download() / 1_000_000
    upload = st.upload() / 1_000_000
    ping = st.results.ping
    return download, upload, ping


def build_payload(device_id: str, download: float, upload: float, ping: float, duration_s: float) -> dict:
    def validate(value: float) -> str:
        if not isinstance(value, (int, float)):
            return "is not a number"
        if value != value or value in (float("inf"), float("-inf")):
            return "is not finite"
        if value < 0:
            return "cannot be negative"
        return ""

    def validate_ping(ping_ms: float) -> str:
        number_error = validate(ping_ms)
        if number_error:
            return number_error
        if ping_ms > 100000:
            return f"ping over 100 seconds? ({ping_ms})"
        return ""

    def validate_upload(upload_mbit_s: float) -> str:
        number_error = validate(upload_mbit_s)
        if number_error:
            return number_error
        if upload_mbit_s > 100000:
            return f"upload over 100000 Mbit/s? ({upload_mbit_s})"
        return ""

    def validate_download(download_mbit_s: float) -> str:
        number_error = validate(download_mbit_s)
        if number_error:
            return number_error
        if download_mbit_s > 100000:
            return f"download over 100000 Mbit/s? ({download_mbit_s})"
        return ""

    def validate_duration(duration_s: float) -> str:
        number_error = validate(duration_s)
        if number_error:
            return number_error
        if duration_s < 1:
            return f"A duration of {duration_s} seconds seems unusually short"
        return ""

    def rounded(value: float) -> float:
        return round(value, 2) if isinstance(value, (int, float)) else value

    payload = build_sensor_payload(
        device_id,
        ("download", rounded(download), validate_download),
        ("upload", rounded(upload), validate_upload),
        ("ping", rounded(ping), validate_ping),
        ("measurement_duration", rounded(duration_s), validate_duration),
    )
    return payload
