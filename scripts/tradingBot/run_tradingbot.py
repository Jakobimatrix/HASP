import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from MQTT.mqtt_client import (
    build_attributes,
    build_client,
    get_enabled_state,
    publish_ack,
    publish_attributes,
    publish_discovery,
    publish_status,
)
from config import DEVICE_ID, TRIGGER_SOURCE
from tradingbot_client import build_payload, run_tradingbot
import config



def main() -> int:
    if not get_enabled_state(config):
        return 0

    started = time.perf_counter()
    client = None
    try:
        client = build_client(config)
        publish_discovery(client, config)
        num_trades = run_tradingbot()
        response_time_ms = (time.perf_counter() - started) * 1000
        payload = build_payload(DEVICE_ID, num_trades)
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
        return 0
    except Exception as exc:  # pragma: no cover
        return 1
    finally:
        if client is not None:
            client.disconnect()


if __name__ == "__main__":
    raise SystemExit(main())
