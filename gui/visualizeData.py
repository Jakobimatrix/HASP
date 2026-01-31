from flask import render_template, request, jsonify
from gui import login_required
from db.devices import get_all_devices
from db.device_data import (
    get_all_keys,
    get_time_series,
    get_xy_series,
)

def register(app):

    @app.route("/visualize", methods=["GET"])
    @login_required
    def visualize():
        devices = get_all_devices()
        return render_template("visualizeData.html", devices=devices)

    @app.route("/api/keys", methods=["POST"])
    @login_required
    def api_keys():
        try:
            data = request.get_json(force=True)
            device_ids = data.get("device_ids", [])
            print("Requested device_ids:", device_ids)
            keys = get_all_keys(device_ids)
            print("Keys fetched:", keys)
            return jsonify(keys)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/data", methods=["POST"])
    @login_required
    def api_data():
        try:
            data = request.get_json(force=True)
            mode = data["mode"]

            if mode == "independent":
                device_ids = data["device_ids"]
                keys = data["keys"]

                result = []

                for device_id in device_ids:
                    for key in keys:
                        rows = get_time_series(device_id, key)
                        result.append({
                            "device_id": device_id,
                            "key": key,
                            "points": [
                                {
                                    "t": r[0] + r[1] / 1e9,
                                    "v": float(r[2]),
                                }
                                for r in rows
                            ]
                        })

                return jsonify(result)

            if mode == "xy":
                device_id = data["device_id"]
                x_key = data["x_key"]
                y_key = data["y_key"]

                rows = get_xy_series(device_id, x_key, y_key)
                return jsonify([
                    {"x": r[0], "y": r[1]}
                    for r in rows
                ])

            return jsonify({"error": "invalid mode"}), 400

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500
