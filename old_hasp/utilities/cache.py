import subprocess

# Simple global cache
RESET_DEVICE_CACHE = {}

def setResetDevice(device_id):
    RESET_DEVICE_CACHE['reset_device_id'] = device_id

def getResetDevice():
    return RESET_DEVICE_CACHE.get('reset_device_id')

def clearResetDevice():
    RESET_DEVICE_CACHE.pop('reset_device_id', None)

def hasMqttBrokerRunning() -> bool:
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "--quiet", "mosquitto"],
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        # systemctl not available (e.g. minimal container)
        return False