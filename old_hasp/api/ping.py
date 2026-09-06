from flask import request, jsonify
from db.devices import deviceExists, updateLastSeen

def register(app):

    """
    API Endpoint:
        POST /api/ping

    Description:
        Receives a device_id in the request JSON, validates it, updates the device's last seen timestamp,
        and returns a simple status response.

    Request JSON:
        {
            "device_id": "<string>"
        }

    Example Input:
        {
            "device_id": "device123"
        }

    Successful Response (HTTP 200):
        {
            "status": "ok"
        }

    Error Response (HTTP 403):
        {
            "error": "invalid device_id"
        }

    Error Cases:
        - Missing "device_id" in the request JSON.
        - "device_id" does not exist in the system.
    """

    @app.route("/api/ping", methods=["POST"])
    def ping():
        data = request.get_json(force=True)
        device_id = data.get("device_id")

        if not device_id or not deviceExists(device_id):
            return jsonify({"error": "invalid device_id"}), 403

        updateLastSeen(device_id)

        return jsonify({"status": "ok"})

