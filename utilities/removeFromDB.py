from db.devices import removeDevice
from db.state import deleteDeviceState
from db.device_data import removeDeviceData
from db.mqtt import getTopicsForDevice, deleteTopic, deleteTopicSchema, deleteTopicSchemaForTopic, deletePayloads
from mqtt.client import unsubscribe

def removeMqttForDevice(device_id):
    topics = getTopicsForDevice(device_id)
    for topic_id, topic_name, has_set, has_state in topics:
        if has_set:
            unsubscribe(f"{device_id}/{topic_name}/set")
        if has_state:
            unsubscribe(f"{device_id}/{topic_name}/state")
        deleteTopicSchemaForTopic(topic_id)
        deleteTopicSchema(topic_id)
        deleteTopic(topic_id)
        deletePayloads(topic_id)


def deleteDevice(device_id):
    removeMqttForDevice(device_id);
    removeDevice(device_id)
    deleteDeviceState(device_id)
    removeDeviceData(device_id)
