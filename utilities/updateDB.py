from utilities.removeFromDB import deleteDevice
from utilities.addToDB import storeOffers
from db.device_data import updateDeviceId
from db.devices import getDevice, updateDevice
from db.mqtt import updateDeviceIdForTopics, getTopicsForDevice
from mqtt.client import subscribe, unsubscribe


def mergeDeviceId(merge_id, device_id):
    topics = getTopicsForDevice(merge_id)
    for topic_id, topic_name, has_set, has_state in topics:
        if has_set:
            unsubscribe(f"{merge_id}/{topic_name}/set")
        if has_state:
            unsubscribe(f"{merge_id}/{topic_name}/state")

    updateDeviceIdForTopics(old_device_id = merge_id, new_device_id = device_id)

    updateDeviceId(old_id = merge_id, new_id = device_id)
    deleteDevice(merge_id)

    for topic_id, topic_name, has_set, has_state in topics:
        if has_set:
            subscribe(f"{device_id}/{topic_name}/set")
        if has_state:
            subscribe(f"{device_id}/{topic_name}/state")    

def updateDevice(device_id, info, offer):
    current_device_data = getDevice(device_id);
    updateDevice(device_id, current_device_data["name"], info, current_device_data["device"])
    return storeOffers(device_id, offer)