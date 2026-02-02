from flask import request, jsonify
import uuid
from db.devices import add_device, device_exists, update_device_definition, get_device
from db.mqtt import add_topic, add_topic_schema, get_topics_for_device, delete_topic, delete_topic_schema, delete_topic_schema_for_topic
from utilities.reset_cache import get_reset_device, clear_reset_device


def store_mqtt_info(device_id, mqtt_offers):
    """
    mqtt_offers: list of dicts, each dict has MQTT topics as keys and list of key definitions as values
    Example:
    [{"esp32/rgb": [{"key_name":"r","value_type":"int","min_value":0,"max_value":255}, ...]}, ...]
    """
    if not mqtt_offers:
        return

    topics = get_topics_for_device(device_id)
    for topic_id, _ in topics:
        delete_topic_schema_for_topic(topic_id)
        delete_topic(topic_id)

    for offer in mqtt_offers:
        for topic_name, keys in offer.items():
            add_topic(device_id, topic_name)
            # Get topic_id to insert schema
            topics = get_topics_for_device(device_id)
            topic_id = next((t[0] for t in topics if t[1] == topic_name), None)
            if topic_id:
                for key in keys:
                    add_topic_schema(
                        topic_id,
                        key_name=key.get("key_name"),
                        value_type=key.get("value_type"),
                        min_value=key.get("min_value"),
                        max_value=key.get("max_value"),
                        enum_values=str(key.get("enum_values")) if key.get("enum_values") else None
                    )

def store_offers(device_id, offers):
    """
    offers: list of dicts, each dict has offer type as key and list of offer details as values
    Example:
    [{"MQTT": [{"topic_name":"esp32/rgb","keys":[{"key_name":"r","value_type":"int","min_value":0,"max_value":255}, ...]}, ...]}]
    """
    if not offers:
        return

    for offer in offers:
        if "MQTT" in offer:
            store_mqtt_info(device_id, offer["MQTT"])
            continue
        # Future offer types can be handled here
                

def register(app):

    """
    API Endpoint:
        POST /api/registerDevice
        POST /api/updateDeviceInfo

    Description:
        Registers a new device with the provided name and definition. Optionally accepts a "hardcoded" device_id, otherwise generates one which the device has to remember for futur calls.
        Validates the device_id, name, and definition.

    Request JSON:
        {
            "name": "<string>",
            "definition": "<string>",
            "device_id": "<string>"  # optional for registerDevice (for hardcoded ids on bare metal) mandatory for updateDeviceInfo
        }

    Example Input_1:
        {
            "name": "SpeedTest",
            "definition": {
                "uses": ["api/reportValues", "api/post/state"],
                "offers": [],
                "info": "Speedtest device reporting internet speed and response time.",
                "Device": "Server"}
        }
    Example Input_2:
        {
            "name": "RGB Light",
            "definition": {
                "uses": ["api/reportValues", "api/post/state"],
                "offers": 
                    [{"MQTT": [
                        "esp32/wake":[{"key_name":"state","value_type":"enum","enum_values":["ON","OFF"]}], 
                        "esp32/brightness":[{"key_name":"brightness","value_type":"float","min_value":0,"max_value":1}],
                        "esp32/rgb":
                            [
                            {"key_name":"r","value_type":"int","min_value":0,"max_value":255},
                            {"key_name":"g","value_type":"int","min_value":0,"max_value":255},
                            {"key_name":"b","value_type":"int","min_value":0,"max_value":255}
                            ],
                        "esp32/hsv":
                            [
                            {"key_name":"h","value_type":"float","min_value":0,"max_value":360},
                            {"key_name":"s","value_type":"float","min_value":0,"max_value":1},
                            {"key_name":"v","value_type":"float","min_value":0,"max_value":1}
                            ],
                        "esp32/effects":[{"key_name":"effect","value_type":"enum","enum_values":["WAVES","RAINBOW","PULSE"]}
                        ]
                    }],
                "info": "RGB Light device.",
                "Device": "ESP32"}
        }

    Successful Response (HTTP 200):
        {
            "device_id": "<string>"
        }

    Error Response (HTTP 403):
        {
            "error": "invalid device_id"
        }

    Error Response (HTTP 400):
        {
            "error": "name and definition required"
        }

    Error Cases:
        - Missing "name" or "definition" in the request JSON.
        - Provided "device_id" does already exist in the system.
    """

    @app.route("/api/registerDevice", methods=["POST"])
    def registerDevice():
        data = request.get_json(force=True)
        name = data.get("name")
        definition = data.get("definition")
        if not name or not definition:
            return jsonify({"error": "name and definition required"}), 400

        reset_id = get_reset_device()
        if reset_id:
            # Reregistering known device, only update definition
            dev = get_device(reset_id)
            if not dev:
                clear_reset_device()
                return jsonify({"error": "Internal Server Error."}), 500

            update_device_definition(reset_id, definition)
            store_offers(reset_id, definition.get("offers", []))
            return jsonify({"device_id": reset_id}), 200

        device_id = data.get("device_id", str(uuid.uuid4()))
        if device_exists(device_id):
            return jsonify({"error": "invalid device_id"}), 403

        add_device(device_id, name, definition)
        store_offers(device_id, definition.get("offers", []))
        return jsonify({"device_id": device_id}), 200

    @app.route("/api/updateDeviceInfo", methods=["POST"])
    def updateDeviceInfo():
        data = request.get_json(force=True)
        device_id = data.get("device_id")
        definition = data.get("definition")
        if not device_id or not definition:
            return jsonify({"error": "device_id and definition required"}), 400
        if not device_exists(device_id):
            return jsonify({"error": "invalid device_id"}), 403

        # Update device definition
        update_device_definition(device_id, definition)

        store_offers(device_id, definition.get("offers", []))
        return jsonify({"device_id": device_id}), 200

