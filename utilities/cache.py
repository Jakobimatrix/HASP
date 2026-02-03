import subprocess

# Simple global cache
RESET_DEVICE_CACHE = {}

def set_reset_device(device_id):
    RESET_DEVICE_CACHE['reset_device_id'] = device_id

def get_reset_device():
    return RESET_DEVICE_CACHE.get('reset_device_id')

def clear_reset_device():
    RESET_DEVICE_CACHE.pop('reset_device_id', None)

def has_mqtt_broker_running() -> bool:
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "--quiet", "mosquitto"],
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        # systemctl not available (e.g. minimal container)
        return False