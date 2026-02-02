from flask import render_template
from db.devices import get_all_devices
from db.state import get_state
from datetime import datetime
from gui import login_required
from utilities.reset_cache import get_reset_device

def register(app):

    @app.route("/devices", endpoint="devices")
    @login_required
    def devices():
        raw_devices = get_all_devices()

        devices = []
        for dev_id, name, last_seen in raw_devices:
            state_row = get_state(dev_id)
            current_state = state_row["current_state"] if state_row and state_row.get("current_state") else None
            requested_state = state_row["requested_state"] if state_row and state_row.get("requested_state") else None
            devices.append({
                "id": dev_id,
                "name": name,
                "last_seen": datetime.fromtimestamp(last_seen).strftime("%Y-%m-%d %H:%M:%S"),
                "current_state": current_state,
                "requested_state": requested_state
            })

        from flask import request, render_template_string
        if request.args.get('ajax') == '1':
            # Only return the table body for AJAX refresh using the macro
            return render_template_string(
                """
                {% from '_devices_table.html' import devices_table %}
                {{ devices_table(devices) }}
                """,
                devices=devices
            )
        return render_template("devices.html", devices=devices, reset_device_id=get_reset_device())
