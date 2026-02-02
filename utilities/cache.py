# Simple global cache for device resets
RESET_DEVICE_CACHE = {}

def set_reset_device(device_id):
    RESET_DEVICE_CACHE['reset_device_id'] = device_id

def get_reset_device():
    return RESET_DEVICE_CACHE.get('reset_device_id')

def clear_reset_device():
    RESET_DEVICE_CACHE.pop('reset_device_id', None)
