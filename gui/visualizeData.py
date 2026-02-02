from flask import render_template, request, jsonify
from gui import login_required
from db.devices import get_all_devices
from db.device_data import (
    get_all_keys,
    get_all_report_ids,
    get_time_series,
    get_xy_series,
    get_time_series_via_report_id,
    get_xy_series_via_report_id,
)

def register(app):

    @app.route("/visualize", methods=["GET"])
    @login_required
    def visualize():
        devices = get_all_devices()
        return render_template("visualizeData.html", devices=devices)

    @app.route("/api/get/reportedValues/keys", methods=["POST"])
    @login_required
    def api_keys():
        try:
            data = request.get_json(force=True)
            device_ids = data.get("device_ids", [])
            keys = get_all_keys(device_ids)
            return jsonify(keys)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/get/reportedValues/report_ids", methods=["POST"])
    @login_required
    def api_report_ids():
        try:
            data = request.get_json(force=True)
            device_ids = data.get("device_ids", [])
            report_ids = get_all_report_ids()
            return jsonify(report_ids)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/get/reportedValues/via_device_id", methods=["POST"])
    @login_required
    def api_data_via_device_id():
        try:
            data = request.get_json(force=True)
            mode = data["mode"]

            if mode == "independent":
                ids = data["device_ids"]

                keys = data["keys"]
                result = []

                
                for id in ids:
                    for key in keys:
                        rows = get_time_series(id, key)

                        device_id = id
                        if not by_device:
                            device_id = rows[3]
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
                id = data["device_id"]

                x_key = data["x_key"]
                y_key = data["y_key"]

                rows = get_xy_series(id, x_key, y_key)
                return jsonify([
                    {"x": r[0], "y": r[1]}
                    for r in rows
                ])

            return jsonify({"error": "invalid mode"}), 400

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/get/reportedValues/via_report_id", methods=["POST"])
    @login_required
    def api_data_via_report_id():
        try:
            data = request.get_json(force=True)
            ids = data["report_ids"]
            result = []
            
            for id in ids:
                rows = get_time_series_via_report_id(id)

                result.append({
                    "device_id": rows[3],
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

            return jsonify({"error": "invalid mode"}), 400

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500