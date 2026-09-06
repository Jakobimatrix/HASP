#!/usr/bin/env python3

import time

from config import DEVICE_ID
from mqtt_client import build_client, publish_ack, publish_attributes, publish_discovery, publish_status
from speedtest_client import build_payload, run_speedtest
from state_manager import is_script_enabled


def main() -> int:
    if not is_script_enabled():
        client = build_client()
        publish_ack(client, "paused")
        client.disconnect()
        return 0

    start = time.perf_counter()
    try:
        client = build_client()
        publish_discovery(client)

        download, upload, ping = run_speedtest()
        response_time_ms = (time.perf_counter() - start) * 1000

        payload = build_payload(DEVICE_ID, download, upload, ping, response_time_ms)
        publish_status(client, payload)
        publish_attributes(client, {
            "source": "cronjob",
            "device_id": DEVICE_ID,
            "response_time_ms": response_time_ms,
            "last_update": int(time.time()),
        })
        publish_ack(client, "running")
        client.disconnect()
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"speedtest failed: {exc}")
        try:
            client.disconnect()
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
