from flask import request, jsonify
from db.devices import deviceExists, updateLastSeen
from utilities.time import Timestamp, getTimeStamp
from db.device_data import insertMeasurements

def handleReportValues(
    *,
    device_id: str,
    key_values: dict,
    ts_sec: int | None = None,
    ts_nsec: int | None = None,
    report_id: str = ""
):
    if not device_id or not deviceExists(device_id):
        raise ValueError("invalid device_id")

    if not isinstance(key_values, dict) or not key_values:
        raise ValueError("no keyValues")

    updateLastSeen(device_id)

    if ts_sec is None:
        ts = getTimeStamp()
        ts_sec = ts.seconds
        ts_nsec = ts.nanoseconds
    else:
        ts_nsec = ts_nsec or 0

    rows = [
        (device_id, ts_sec, ts_nsec, key, value, report_id)
        for key, value in key_values.items()
    ]

    insertMeasurements(rows)

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

        try:
            handleReportValues(
                device_id=data.get("device_id"),
                key_values=data.get("keyValues"),
                ts_sec=data.get("s"),
                ts_nsec=data.get("ns"),
                report_id=data.get("report_id")
            )
        except ValueError as e:
            msg = str(e)
            status = 403 if "device_id" in msg else 400
            return jsonify({"error": msg}), status

        return jsonify({"status": "ok"}), 200

