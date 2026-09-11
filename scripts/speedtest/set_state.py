#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
from config import DEVICE_ID
from MQTT.mqtt_client import build_client, publish_control


def main() -> int:
    parser = argparse.ArgumentParser(description="Set local enabled state for speedtest cronjob.")
    parser.add_argument("--enabled", choices=["true", "false"], required=True)
    args = parser.parse_args()

    enabled = args.enabled == "true"
    client = build_client(config)
    try:
        publish_control(client, config, enabled, "local-script")
    finally:
        client.disconnect()
    print(f"State set to {enabled} for {DEVICE_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
