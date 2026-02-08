from flask import request, jsonify
import json

from utilities.cache import hasMqttBrokerRunning
from mqtt.client import publish as mqtt_publish
from db.mqtt import addTopicPayload, get_or_create_topic


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

        if not hasMqttBrokerRunning():
            return jsonify({"error": "MQTT broker not running"}), 503

        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        device_id = data.get("device_id")
        topic = data.get("topic")
        values = data.get("values")

        if not device_id or not topic or not isinstance(values, dict):
            return jsonify({"error": "Missing or invalid parameters"}), 400

        try:
            payload_str = json.dumps(values)

            # Publish via shared MQTT client
            mqtt_publish(topic, payload_str)

            # Persist payload (use topic_id, not topic string)
            topic_id = get_or_create_topic(device_id, topic)
            addTopicPayload(topic_id, payload_str)

            return jsonify({"success": True}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
