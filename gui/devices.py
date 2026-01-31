from flask import render_template
from db.devices import get_all_devices
from datetime import datetime
from gui import login_required

def register(app):

    @app.route("/devices", endpoint="devices")
    @login_required
    def devices():
        raw_devices = get_all_devices()

        devices = []
        for dev_id, name, last_seen in raw_devices:
            devices.append({
                "id": dev_id,
                "name": name,
                "last_seen": datetime.fromtimestamp(last_seen).strftime("%Y-%m-%d %H:%M:%S")
            })

        return render_template("devices.html", devices=devices)
