from flask import request, jsonify
from db.devices import device_exists, update_last_seen
from utilities.time_utils import Timestamp, get_timestamp

def register(app):

    """
    API Endpoint:
        POST /api/reportValues

    Description:
        Receives a device_id and key-value pairs in the request JSON, validates the device, updates the device's last seen timestamp,
        and stores the reported values with a timestamp. Optionally accepts a timestamp and report_id. report_id can be used to cluster related measurements.

    Request JSON:
        {
            "device_id": "<string>",
            "keyValues": {"key1": value1, ...},
            "s": <int>,         # optional, seconds since epoch
            "ns": <int>,        # optional, nanoseconds
            "report_id": "<string>"  # optional
        }

    Example Input:
        {
            "device_id": "device123",
            "keyValues": {"temperature": 22.5, "humidity": 60}
        }

    Successful Response (HTTP 200):
        {
            "status": "ok"
        }

    Error Response (HTTP 403):
        {
            "error": "invalid device_id"
        }

    Error Response (HTTP 400):
        {
            "error": "no keyValues"
        }

    Error Cases:
        - Missing "device_id" in the request JSON.
        - "device_id" does not exist in the system.
        - Missing or invalid "keyValues" in the request JSON.
    """

    @app.route("/api/reportValues", methods=["POST"])
    def reportValues():
        data = request.get_json(force=True)
        device_id = data.get("device_id")

        if not device_id or not device_exists(device_id):
            return jsonify({"error": "invalid device_id"}), 403

        update_last_seen(device_id)

       # Timestamp handling
        if "s" in data:
            ts_sec = int(data["s"])
            ts_nsec = int(data.get("ns", 0))
        else:
            ts = get_timestamp()
            ts_sec = ts.seconds
            ts_nsec = ts.nanoseconds

        key_values = data.get("keyValues")
        if not isinstance(key_values, dict) or not key_values:
            return jsonify({"error": "no keyValues"}), 400

        report_id = data.get("report_id") or uuid.uuid4().hex

        rows = []
        for key, value in key_values.items():
            rows.append(
                (device_id, ts_sec, ts_nsec, key, value, report_id)
            )

        insert_measurements(rows)

