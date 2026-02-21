import json
import threading
import paho.mqtt.client as mqtt

from db.mqtt import addTopicPayload, get_or_create_topic, getAllTopics
from api.reportValues import handleReportValues
from api.state import handleDeviceState
from api.registerDevice import handleRegisterOrUpdateDevice

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

_client = None

def onConnect(client, userdata, flags, rc):
    print("MQTT connected:", rc)


def publishApiResponse(device_id, topic, apiResponse):
    publish(f"{device_id}/api/{topic}", apiResponse)

def tryDefaultMessages(msg, payload) -> bool:
   device_id = payload.get("device_id")

    if msg.topic == "/api/reportValues":
        try:
            handleReportValues(
                device_id=device_id,
                key_values=payload.get("keyValues"),
                ts_sec=payload.get("s"),
                ts_nsec=payload.get("ns"),
                report_id=payload.get("report_id")
            )
            publishApiResponse(device_id, "reportValues", {"status": "ok"})
        except ValueError as e:
            publishApiResponse(device_id, "reportValues", {"error": str(e)})
        return True

    if topic == "api/registerDevice":
        temp_id = payload.get("temp_id")
        if not temp_id:
            return True # ignore, i dont know where to send a response
        try:
            device_id = handleRegisterOrUpdateDevice(
                name=payload.get("name"),
                device_id=device_id,
                info=payload.get("info"),
                device=payload.get("device"),
                offers_string=json.dumps(payload.get("offers", [])),
                allow_create=True
            )
            publishApiResponse(temp_id, "registerDevice", jsonify({"device_id": device_id}))
        except ValueError as e:
            publishApiResponse(temp_id, "registerDevice", {"error": str(e)})
        return True

    if topic == "api/updateDeviceInfo":
        try:
            device_id = handleRegisterOrUpdateDevice(
                device_id=device_id,
                info=payload.get("info"),
                offers_string=json.dumps(payload.get("offers", [])),
                allow_create=False
            )
            publishApiResponse(temp_id, "updateDeviceInfo", jsonify({"device_id": device_id}))
        except ValueError as e:
            publishApiResponse(temp_id, "updateDeviceInfo", {"error": str(e)})
        return True

    if topic == "api/post/state":
        try:
            handleDeviceState(
                device_id=device_id,
                current_state=payload.get("current_state"),
                possible_states=payload.get("possible_states")
            )
            publishApiResponse(device_id, "post/state", {"status": "ok"})
        except ValueError as e:
            publishApiResponse(device_id, "post/state", {"error": str(e)})
        return True
    
    return False

def onMessage(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
    except Exception:
        return  # ignore invalid payloads

    if tryDefaultMessages(msg, payload):
        return

    topic = msg.topic.strip("/")
    parts = topic.split("/")

    # Expected: <device_id>/<topic_name>/state
    if len(parts) != 3:
        return

    device_id, topic_name, endpoint = parts

    if endpoint != "state":
        return  # we only accept state updates

    if not deviceExists(device_id):
        return

    topic_id = getTopicIdForDevice(device_id, topic_name)
    if not topic_id:
        return

    addTopicPayload(topic_id, json.dumps(payload))
    updateLastSeen(device_id)

def startMqtt():
    global _client
    _client = mqtt.Client()
    _client.on_connect = on_connect
    _client.on_message = on_message

    _client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)

    _client.loop_start()

    topics = getAllTopics()
    for device_id, topic_name, has_set, has_state in topics:
        if has_set:
            subscribe(f"{device_id}/{topic_name}/set")
        if has_state:
            subscribe(f"{device_id}/{topic_name}/state")

    subscribe(f"api/registerDevice")
    subscribe(f"api/updateDeviceInfo")
    subscribe(f"api/reportValues")
    subscribe(f"api/post/state")

def publish(topic, payload, retain=False):
    if _client:
        _client.publish(topic, payload, retain=retain)

def subscribe(topic, qos=0):
    if _client and topic not in _subscriptions:
        _client.subscribe(topic, qos=qos)
        _subscriptions.add(topic)

def unsubscribe(topic):
    if _client and topic in _subscriptions:
        _client.unsubscribe(topic)
        _subscriptions.remove(topic)