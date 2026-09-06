#!/usr/bin/env python3

import json
import os

from config import CONTROL_TOPIC, DEFAULT_ENABLED, LOCAL_STATE_FILE


def read_local_state() -> bool:
    if not os.path.exists(LOCAL_STATE_FILE):
        return DEFAULT_ENABLED

    try:
        with open(LOCAL_STATE_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            return bool(data.get("enabled", DEFAULT_ENABLED))
        if isinstance(data, bool):
            return data
    except (OSError, ValueError, TypeError):
        pass

    return DEFAULT_ENABLED


def write_local_state(enabled: bool) -> None:
    with open(LOCAL_STATE_FILE, "w", encoding="utf-8") as handle:
        json.dump({"enabled": bool(enabled)}, handle)


def is_script_enabled() -> bool:
    return read_local_state()


def set_script_state(enabled: bool) -> None:
    write_local_state(enabled)


def control_payload(enabled: bool) -> str:
    return json.dumps({"enabled": bool(enabled), "source": "ha"})
