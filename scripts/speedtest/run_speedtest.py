#!/usr/bin/env python3

import json
import time

from config import DEVICE_ID
from mqtt_client import build_client, publish_ack, publish_attributes, publish_discovery, publish_status
from speedtest_client import build_payload, run_speedtest
from state_manager import parse_enabled_payload, control_topic


def get_enabled_state() -> bool:
    client = None
    try:
        client = build_client()
        topic = control_topic()

        # Read the retained payload if present; if none exists, default to enabled.
        # MQTT retains the last message on that topic, so this acts like a stored state.
        payload = client.publish(topic, None, retain=True)
        # publish() is fire-and-forget; to read retained state, we need a subscriber callback.
        # We therefore use a short-lived client and wait for the last retained message.
        state = {"enabled": True}

        def on_message(client_obj, userdata, msg):
            nonlocal state
            try:
                state = json.loads(msg.payload.decode("utf-8"))
            except Exception:
                state = {"enabled": True}

        client.on_message = on_message
        client.subscribe(topic)
        client.loop_start()
        time.sleep(0.5)
        client.loop_stop()
        client.disconnect()

        return bool(parse_enabled_payload(json.dumps(state)))
    except Exception:
        return False


def main() -> int:
    enabled = get_enabled_state()
    if not enabled:
        print("Skip speedtest: MQTT control state disabled")
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
