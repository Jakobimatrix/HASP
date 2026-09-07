#!/usr/bin/env python3

import json

from config import CONTROL_TOPIC


def parse_enabled_payload(payload: str) -> bool:
    try:
        data = json.loads(payload)
        if isinstance(data, dict):
            return bool(data.get("enabled", True))
        if isinstance(data, bool):
            return data
    except (TypeError, ValueError):
        pass
    return True


def control_payload(enabled: bool) -> str:
    return json.dumps({"enabled": bool(enabled), "source": "ha"})


def control_topic() -> str:
    return CONTROL_TOPIC
