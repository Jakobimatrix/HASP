from flask import request, jsonify
import uuid
from db.devices import add_device, device_exists

def register(app):

    """
    API Endpoint:
        POST /api/registerDevice

    Description:
        Registers a new device with the provided name and definition. Optionally accepts a "hardcoded" device_id, otherwise generates one which the device has to remember for futur calls.
        Validates the device_id, name, and definition.

    Request JSON:
        {
            "name": "<string>",
            "definition": "<string>",
            "device_id": "<string>"  # optional
        }

    Example Input:
        {
            "name": "Device Name",
            "definition": "Device Definition"
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
        device_id = data.get("device_id", str(uuid.uuid4()))
        if device_exists(device_id):
            return jsonify({"error": "invalid device_id"}), 403
            
        if not name or not definition:
            return jsonify({"error": "name and definition required"}), 400
        
        add_device(device_id, name, definition)

        return jsonify({
            "device_id": device_id
        })
