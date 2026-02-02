
from flask import render_template, request, redirect, url_for, flash
from datetime import datetime

from gui import login_required
from db.devices import get_all_devices, get_device, update_device_name, delete_device
from db.state import get_state, delete_state
from db.device_data import count_device_data, delete_device_data, update_device_id
from utilities.reset_cache import set_reset_device


def register(app):

    @app.route("/manageDevice/<device_id>", endpoint="manageDevice", methods=["GET", "POST"])
    @login_required
    def manage_device(device_id=None):
        device = get_device(device_id)
        if not device:
            flash("Device not found.", "danger")
            return redirect(url_for("devices"))
        device["last_seen"] = datetime.fromtimestamp(device["last_seen"]).strftime("%Y-%m-%d %H:%M:%S")
        state = get_state(device_id)
        data_count = count_device_data(device_id)
        # For merge dropdown: all other devices
        all_devices = get_all_devices()
        other_devices = [d for d in all_devices if d[0] != device_id]
        other_devices = [{"id": d[0], "name": d[1]} for d in other_devices]

        if request.method == "POST":
            action = request.form.get("action")
            if action == "rename":
                new_name = request.form.get("new_name")
                if new_name:
                    update_device_name(device_id, new_name)
                    flash("Device renamed.", "success")
                    return redirect(url_for("manageDevice", device_id=device_id))
            elif action == "delete":
                delete_device(device_id)
                delete_state(device_id)
                delete_device_data(device_id)
                flash("Device and all data deleted.", "success")
                return redirect(url_for("devices"))
            elif action == "merge":
                merge_id = request.form.get("merge_device_id")
                if merge_id and merge_id != device_id:
                    update_device_id(merge_id, device_id)
                    delete_device(merge_id)
                    delete_state(merge_id)
                    flash(f"Merged device {merge_id} into {device_id}.", "success")
                    return redirect(url_for("manageDevice", device_id=device_id))
            elif action == "reset":
                # Set reset_mode for UI, set global cache
                set_reset_device(device_id)
                return redirect(url_for("devices"))

        return render_template(
            "manage_device.html",
            device=device,
            state=state,
            data_count=data_count,
            other_devices=other_devices
        )