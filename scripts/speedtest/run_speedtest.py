#!/usr/bin/env python3

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
from MQTT.mqtt_client import build_client, get_enabled_state, publish_ack, publish_attributes, publish_discovery, publish_status, build_attributes
from config import DEVICE_ID, TRIGGER_SOURCE
from speedtest_client import build_payload, run_speedtest


def main() -> int:
    enabled = get_enabled_state(config)
    if not enabled:
        return 0

    start = time.perf_counter()
    client = None
    try:
        client = build_client(config)
        publish_discovery(client, config)

        download, upload, ping = run_speedtest()
        response_time_ms = (time.perf_counter() - start) * 1000

        payload = build_payload(DEVICE_ID, download, upload, ping, response_time_ms)
        publish_status(client, config, payload)
        publish_attributes(
            client,
            config,
            build_attributes(
                TRIGGER_SOURCE,
                DEVICE_ID,
                response_time_ms,
                payload,
            ),
        )
        publish_ack(client, config, "running")
        client.disconnect()
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"speedtest failed: {exc}")
        try:
          if client is not None:
              client.disconnect()
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
