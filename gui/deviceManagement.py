
from flask import render_template, request, redirect, url_for, flash, request, render_template_string

from datetime import datetime
import json

from gui import login_required
from db.devices import getAllDevices, getDevice, updateDeviceName, removeDevice
from db.state import getDeviceState, deleteDeviceState
from db.device_data import countDeviceData, removeDeviceData, updateDeviceId
from utilities.cache import setResetDevice
from utilities.time import seconds2FormatedTime
from db.mqtt import getAllTopicsForDevice, getLatestPayload
from utilities.cache import hasMqttBrokerRunning
from utilities.removeFromDB import deleteDevice
from utilities.updateDB import mergeDeviceId


def register(app):

    @app.route("/manageDevice/<device_id>", endpoint="manageDevice", methods=["GET", "POST"])
    @login_required
    def manage_device(device_id=None):
        device = getDevice(device_id)
        if not device:
            flash("Device not found.", "danger")
            return redirect(url_for("devices"))
        device["last_seen"] = seconds2FormatedTime(device["last_seen"])
        state = getDeviceState(device_id)
        data_count = countDeviceData(device_id)
        # For merge dropdown: all other devices
        all_devices = getAllDevices()
        other_devices = [d for d in all_devices if d[0] != device_id]
        other_devices = [{"id": d[0], "name": d[1]} for d in other_devices]

        if request.method == "POST":
            action = request.form.get("action")
            if action == "rename":
                new_name = request.form.get("new_name")
                if new_name:
                    updateDeviceName(device_id, new_name)
                    flash("Device renamed.", "success")
                    return redirect(url_for("manageDevice", device_id=device_id))
            elif action == "delete":
                deleteDevice(device_id)
                flash("Device and all data deleted.", "success")
                return redirect(url_for("devices"))
            elif action == "merge":
                merge_id = request.form.get("merge_device_id")
                if merge_id and merge_id != device_id:
                    mergeDeviceId(merge_id = merge_id, device_id = device_id)
                    flash(f"Merged device {merge_id} into {device_id}.", "success")
                    return redirect(url_for("manageDevice", device_id=device_id))
            elif action == "reset":
                # Set reset_mode for UI, set global cache
                setResetDevice(device_id)
                return redirect(url_for("devices"))

        show_mqtt = hasMqttBrokerRunning()

        mqtt_topics = []
        last_values = {}
        if show_mqtt:
            #todo
            for topic_row in getAllTopicsForDevice(device_id):
                mqtt_topics.append({
                    "name": topic_row["name"],
                    "id": topic_row["id"],
                    "keys": topic_row["keys"]
                })
            
            for topic in mqtt_topics:
                latest = getLatestPayload(topic["id"])
                if latest:
                    last_values[topic["name"]] = json.loads(latest["payload"])
                else:
                    last_values[topic["name"]] = {}

        if not mqtt_topics or len(mqtt_topics) == 0:
            show_mqtt = False

        if request.args.get('ajax') == '1':
            # Only return the table body for AJAX refresh using the macro
            return render_template_string(
                """
                {% from '_devices_table.html' import devices_table %}
                {{ devices_table(devices) }}
                """,
                devices=devices
            )

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