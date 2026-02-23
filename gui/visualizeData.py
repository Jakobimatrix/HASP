from flask import render_template, request, jsonify
from gui import login_required
from db.devices import getAllDevices
from db.device_data import (
    getAllKeys,
    getAllReportIds,
    getTimeSeries,
    getXYSeries,
    getTimeSeriesViaReportId,
    getAllDataWithAReportId
)

def register(app):

    @app.route("/visualize", methods=["GET"])
    @login_required
    def visualize():
        devices = getAllDevices()
        return render_template("visualizeData.html", devices=devices)

    @app.route("/api/get/reportedValues/keys", methods=["POST"])
    @login_required
    def api_keys():
        try:
            data = request.get_json(force=True)
            device_ids = data.get("device_ids", [])
            keys = getAllKeys(device_ids)
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
            report_ids = getAllReportIds()
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
            result = []
            if mode == "independent":
                device_ids = data["device_ids"]
                keys = data["keys"]
                for device_id in device_ids:
                    for key in keys:
                        rows = getTimeSeries(device_id, key)
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
            elif mode == "xy":
                id = data["device_id"]

                x_key = data["x_key"]
                y_key = data["y_key"]

                rows = getXYSeries(id, x_key, y_key)
                result.append({
                    "x_key": x_key,
                    "y_key": y_key,
                    "points": [
                        {"x": float(r[0]), "y": float(r[1])}
                        for r in rows
                    ]
                })
            else:
                return jsonify({"error": "invalid mode"}), 400

            return jsonify(result)


        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/get/reportedValues/via_report_id", methods=["POST"])
    @login_required
    def api_data_via_report_id():
        try:
            data = request.get_json(force=True)
            ids = data["keys"]  # in this case keys are report_ids
            result = []

            grouped = {}
            rows = []
            reprgivenIds = []
            
            for id in ids:
                rows = getTimeSeriesViaReportId(id)
                reprgivenIds.append(repr(id))
                
                for r in rows:
                    key = r[3] + ":" + r[4]  # device_id:key
                    if key not in grouped:
                        grouped[key] = []
                    grouped[key].append(r)

                for key, groupedRows in grouped.items():
                    result.append({
                        "device_id": groupedRows[0][2] + ":" + id,
                        "key": groupedRows[0][3] + ":" + id,
                        "points": [
                            {
                                "t": r[0] + r[1] / 1e9,
                                "v": float(r[4])
                            }
                            for r in groupedRows
                        ]
                    })
            #return jsonify(result)
            allDataWithReportId = getAllDataWithAReportId()
            reprallData_ids = []

            for r in allDataWithReportId:
                reprallData_ids.append(repr(r[5]))  # r[5] is the report_id


            return jsonify({"data": result, "report_ids": ids, "debug_rows": rows, "debug_groups": grouped, "repr_given_ids": reprgivenIds, "repr_all_ids": reprallData_ids})

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500