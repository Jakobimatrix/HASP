from flask import request, jsonify
import json
import paho.mqtt.publish as publish
from db.mqtt import add_topic_payload
from utilities.cache import has_mqtt_broker_running

def register(app):
    @app.route("/api/send/mqtt", methods=["POST"])
    def send_mqtt():
        """
        Expects JSON:
        {
            "device_id": "<string>",
            "topic": "<string>",
            "values": { "key1": value1, "key2": value2, ... }
        }
        """

        if not has_mqtt_broker_running():
            return jsonify({"error": "MQTT broker not running"}), 500

        data = request.get_json(force=True)
        device_id = data.get("device_id")
        topic = data.get("topic")
        values = data.get("values")

        if not device_id or not topic or not values:
            return jsonify({"error": "Missing parameters"}), 400

        try:
            # Convert the dict of key/values into JSON string payload
            payload_str = json.dumps(values)

            # Publish to MQTT broker
            publish.single(topic, payload_str, hostname="YOUR_MQTT_BROKER_IP")

            # Store payload in the database (history)
            add_topic_payload(topic_id=topic, payload=payload_str)

            return jsonify({"success": True}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
