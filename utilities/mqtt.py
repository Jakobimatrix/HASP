from mqtt.client import start_mqtt
from db.mqtt import getAllTopics
from mqtt.client import subscribe

def startMqtt():
    start_mqtt()
    topics = getAllTopics()
    for device_id, topic_name, has_set, has_state in topics:
        if has_set:
            subscribe(f"{device_id}/{topic_name}/set")
        if has_state:
            subscribe(f"{device_id}/{topic_name}/state")
