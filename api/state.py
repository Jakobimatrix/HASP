from flask import Blueprint, request, jsonify
import time
import db.state as state_db

bp = Blueprint('state_api', __name__, url_prefix='/api')

@bp.route('/state', methods=['POST'])
def report_state():
    data = request.get_json()
    device_id = data.get('device_id')
    current_state = data.get('current_state')
    possible_states = data.get('possible_states')
    if not (device_id and current_state and possible_states):
        return jsonify({'error': 'Missing required fields'}), 400

    # Save or update state in DB
    state_db.set_state(device_id, current_state, possible_states)
    # Get full state row
    row = state_db.get_state(device_id)
    now = int(time.time())
    requested_state = row.get('requested_state')
    requested_state_start = row.get('requested_state_start')
    requested_state_expire = row.get('requested_state_expire')
    # Logic for state selection
    if requested_state and requested_state in possible_states:
        start_ok = (requested_state_start is None) or (requested_state_start == 0) or (now >= requested_state_start)
        expire_ok = (requested_state_expire is None) or (requested_state_expire == 0) or (now <= requested_state_expire)
        if start_ok and expire_ok:
            return jsonify({'state': requested_state}), 200
        # If not valid, clear requested_state
        state_db.update_requested_state(device_id, None, None, None)
    return jsonify({'state': current_state}), 200

@bp.route('/state', methods=['GET'])
def get_state():
    device_id = request.args.get('device_id')
    if not device_id:
        return jsonify({'error': 'Missing device_id'}), 400
    row = state_db.get_state(device_id)
    if not row:
        return jsonify({'error': 'Device not found'}), 404
    return jsonify(row)
