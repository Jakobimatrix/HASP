from flask import render_template, request, render_template_string
from db.devices import getAllDevices
from db.state import getDeviceState
from datetime import datetime
from gui import login_required
from utilities.cache import getResetDevice
from utilities.time import seconds2FormatedTime


def register(app):

    @app.route("/devices", endpoint="devices")
    @login_required
    def devices():
        raw_devices = getAllDevices()

        devices = []
        for dev_id, name, last_seen in raw_devices:
            state_row = getDeviceState(dev_id)
            current_state = state_row["current_state"] if state_row and state_row.get("current_state") else None
            requested_state = state_row["requested_state"] if state_row and state_row.get("requested_state") else None
            devices.append({
                "id": dev_id,
                "name": name,
                "last_seen": seconds2FormatedTime(last_seen),
                "current_state": current_state,
                "requested_state": requested_state
            })

        if request.args.get('ajax') == '1':
            # Only return the table body for AJAX refresh using the macro
            return render_template_string(
                """
                {% from '_devices_table.html' import devices_table %}
                {{ devices_table(devices) }}
                """,
                devices=devices
            )
        return render_template("devices.html", devices=devices, reset_device_id=getResetDevice())
