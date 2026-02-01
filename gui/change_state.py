from flask import render_template, request, redirect, url_for, flash
import db.state as state_db
import time
import json
from gui import login_required

def register(app):
    @app.route("/change_state/<device_id>", methods=["GET", "POST"], endpoint="change_state_view")
    @login_required
    def change_state_view(device_id):
        row = state_db.get_state(device_id)
        if not row:
            flash('Device not found', 'error')
            return render_template('change_state.html', device_id=device_id, possible_states=[], current_state=None, requested_state=None, requested_state_start=None, requested_state_expire=None, save_dates=False)

        possible_states = row.get('possible_states', [])
        current_state = row.get('current_state')
        requested_state = row.get('requested_state')
        requested_state_start = row.get('requested_state_start')
        requested_state_expire = row.get('requested_state_expire')

        if request.method == 'POST':
            new_state = request.form.get('requested_state')
            save_dates = request.form.get('save_dates') == 'on'
            start = request.form.get('requested_state_start')
            expire = request.form.get('requested_state_expire')
            start_ts = int(time.mktime(time.strptime(start, '%Y-%m-%dT%H:%M'))) if start else None
            expire_ts = int(time.mktime(time.strptime(expire, '%Y-%m-%dT%H:%M'))) if expire else None
            if new_state and new_state in possible_states:
                if save_dates:
                    state_db.update_requested_state(device_id, new_state, start_ts, expire_ts)
                else:
                    state_db.update_requested_state(device_id, new_state, None, None)
                flash('Requested state updated.', 'success')
                return redirect(url_for('change_state_view', device_id=device_id))
            else:
                flash('Invalid state selected.', 'error')

        return render_template('change_state.html',
            device_id=device_id,
            possible_states=possible_states,
            current_state=current_state,
            requested_state=requested_state,
            requested_state_start=requested_state_start,
            requested_state_expire=requested_state_expire,
            save_dates=False
        )
