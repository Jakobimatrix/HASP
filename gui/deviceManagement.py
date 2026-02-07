
from flask import render_template, request, redirect, url_for, flash
from datetime import datetime
import json

from gui import login_required
from db.devices import get_all_devices, get_device, update_device_name, delete_device
from db.state import get_state, delete_state
from db.device_data import count_device_data, delete_device_data, update_device_id
from utilities.cache import set_reset_device
from utilities.time_utils import seconds2FormatedTime
from db.mqtt import get_all_topics_for_device, get_latest_payload
from utilities.cache import has_mqtt_broker_running


def register(app):

    @app.route("/manageDevice/<device_id>", endpoint="manageDevice", methods=["GET", "POST"])
    @login_required
    def manage_device(device_id=None):
        device = get_device(device_id)
        if not device:
            flash("Device not found.", "danger")
            return redirect(url_for("devices"))
        device["last_seen"] = seconds2FormatedTime(device["last_seen"])
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

        show_mqtt = has_mqtt_broker_running()

        mqtt_topics = []
        last_values = {}
        if show_mqtt:
            for topic_row in get_all_topics_for_device(device_id):
                # topic_row = dict(id=..., name=..., keys=json_string)
                keys = json.loads(topic_row["keys"])  # keys stored as JSON in DB
                mqtt_topics.append({
                    "name": topic_row["name"],
                    "keys": keys
                })
            
            for topic in mqtt_topics:
                latest = get_latest_payload(topic["name"])
                if latest:
                    last_values[topic["name"]] = json.loads(latest["payload"])
                else:
                    last_values[topic["name"]] = {}

        if empty(mqtt_topics):
            show_mqtt = False

        return render_template(
            "manage_device.html",
            device=device,
            state=state,
            data_count=data_count,
            other_devices=other_devices,
            mqtt_topics=mqtt_topics,
            last_values=last_values,
            show_mqtt=show_mqtt
        )