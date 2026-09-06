#!/usr/bin/env python3

import json
import time

import speedtest


def run_speedtest() -> tuple[float, float, float]:
    st = speedtest.Speedtest(secure=True)
    st.get_best_server()
    download = st.download() / 1_000_000
    upload = st.upload() / 1_000_000
    ping = st.results.ping
    return download, upload, ping


def build_payload(device_id: str, download: float, upload: float, ping: float, response_time_ms: float) -> dict:
    return {
        "device_id": device_id,
        "download": round(download, 2),
        "upload": round(upload, 2),
        "ping": round(ping, 2),
        "response_time_ms": round(response_time_ms, 2),
        "timestamp": int(time.time()),
    }
