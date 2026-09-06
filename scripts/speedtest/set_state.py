#!/usr/bin/env python3

import argparse

from config import CONTROL_TOPIC, DEVICE_ID
from mqtt_client import build_client, publish_disabled_message
from state_manager import set_script_state


def main() -> int:
    parser = argparse.ArgumentParser(description="Set local enabled state for speedtest cronjob.")
    parser.add_argument("--enabled", choices=["true", "false"], required=True)
    args = parser.parse_args()

    enabled = args.enabled == "true"
    set_script_state(enabled)

    client = build_client()
    client.publish(CONTROL_TOPIC, __import__("json").dumps({"enabled": enabled, "source": "local-script"}), retain=True)
    client.disconnect()
    print(f"State set to {enabled} for {DEVICE_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
