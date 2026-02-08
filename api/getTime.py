from flask import request, jsonify
from db.devices import deviceExists, updateLastSeen
from utilities.time import Timestamp, getTimeStamp


def register(app):
    """
    API Endpoint:
        POST /api/getTime

    Description:
        Receives a device_id in the request JSON, validates it, updates the device's last seen timestamp,
        and returns the current server time in seconds and nanoseconds.

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
            "status": "ok",
            "s": 1717689600,      # Example: seconds since epoch
            "ns": 1717689600123456789  # Example: nanoseconds timestamp
        }

    Error Response (HTTP 403):
        {
            "error": "invalid device_id"
        }

    Error Cases:
        - Missing "device_id" in the request JSON.
        - "device_id" does not exist in the system.
    """

    @app.route("/api/getTime", methods=["POST"])
    def getTime():
        data = request.get_json(force=True)
        device_id = data.get("device_id")

        if not device_id or not deviceExists(device_id):
            return jsonify({"error": "invalid device_id"}), 403

        updateLastSeen(device_id)

        ts = getTimeStamp()

        return jsonify({"status": "ok", "s": ts.seconds, "ns": ts})

