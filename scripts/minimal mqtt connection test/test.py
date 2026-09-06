#!/usr/bin/env python3

import json, time
import paho.mqtt.client as mqtt

c = mqtt.Client()
c.username_pw_set("mqtt2HA", "test")
c.connect("192.168.178.106", 1883, 60)

payload = {
    "name": "device123_download",
    "state_topic": "devices/device123/speedtest",
    "unique_id": "device123_download_001",
    "value_template": "{{ value_json.download }}",
    "unit_of_measurement": "Mbit/s"
}

c.publish("homeassistant/sensor/device123_download/config", json.dumps(payload), retain=True)
print("sent")
c.disconnect()