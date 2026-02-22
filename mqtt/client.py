import json
import threading
import paho.mqtt.client as mqtt

from db.mqtt import addTopicPayload, getAllTopics, getTopicId
from api.reportValues import handleReportValues
from api.state import handleDeviceState
from api.registerDevice import handleRegisterOrUpdateDevice

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

_client = None

def subscribe(topic, qos=0):
    if _client and topic not in _subscriptions:
        _client.subscribe(topic, qos=qos)
        _subscriptions.add(topic)

def unsubscribe(topic):
    if _client and topic in _subscriptions:
        _client.unsubscribe(topic)
        _subscriptions.remove(topic)

def unsubscribeState(device_id, topic_name):
    unsubscribe(f"{device_id}/{topic_name}/state")

def subscribeState(device_id, topic_name):
    subscribe(f"{device_id}/{topic_name}/state")


def onConnect(client, userdata, flags, rc):
    print("MQTT connected:", rc)


def publish(topic, payload, retain=False):
    if _client:
        _client.publish(topic, payload, retain=retain)

def publishApiResponse(device_id, topic, apiResponse):
    publish(f"{device_id}/api/{topic}", apiResponse)

def publishSet(device_id, topic_name, key_values):
    publish(f"{device_id}/{topic_name}/set", json.dumps(key_values))


def updateTopicState(device_id, topic_name, payload):
    topic_id = getTopicId(device_id, topic_name)
    if topic_id:
        addTopicPayload(topic_id, payload)
        return

    print(f"Received MQTT state update for unknown topic: {device_id}/{topic_name} with payload: {payload}")


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
        print("Failed to decode MQTT message payload as JSON:", msg.payload)
        return

    if msg.topic.startswith("api/"):
        if tryDefaultMessages(msg, payload):
            return
        else:
            print("Received message for unknown API endpoint:", msg.topic)
            return

    topic = msg.topic.strip("/")
    parts = topic.split("/")

    # Expected: <device_id>/<topic_name>/state
    if len(parts) != 3:
        print("Received MQTT message with invalid topic format:", msg.topic)
        return

    device_id, topic_name, endpoint = parts

    if endpoint != "state":
        print("Received MQTT message for unsupported endpoint:", endpoint)
        return

    if not deviceExists(device_id):
        print("Received MQTT message for unknown device_id:", device_id)
        return
    
    updateTopicState(device_id, topic_name, payload)
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
        if has_state:
            subscribeState(device_id, topic_name)

    subscribe(f"api/registerDevice")
    subscribe(f"api/updateDeviceInfo")
    subscribe(f"api/reportValues")
    subscribe(f"api/post/state")

