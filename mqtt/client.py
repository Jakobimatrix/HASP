import json
import threading
import paho.mqtt.client as mqtt

from db.mqtt import addTopicPayload, get_or_create_topic

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

_client = None

def on_connect(client, userdata, flags, rc):
    print("MQTT connected:", rc)

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode(errors="ignore")

    # Example: persist payload
    
    topic_id = get_or_create_topic(topic)
    addTopicPayload(topic_id, payload)

def start_mqtt():
    global _client
    _client = mqtt.Client()
    _client.on_connect = on_connect
    _client.on_message = on_message

    _client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)

    # IMPORTANT: non-blocking loop
    _client.loop_start()

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