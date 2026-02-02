from flask import request, jsonify
import time
import db.state as state_db


def register(app):
    """
    API Endpoints:
        POST /api/post/state
        GET /api/get/state

    Description:
        POST: Receives device_id, current_state, possible_states. Returns requested_state if valid, else current_state.
        GET: Returns full state info for a device_id.

    Request JSON: /api/post/state
        {
            "device_id": "<string>",
            "current_state": "<string>",
            "possible_states": ["state1", "state2", ...]
        }

    Successful POST Response (HTTP 200):
        {
            "state": "<string>"  # requested_state if valid, else current_state
        }

    REQUEST JSON: /api/get/state
        {
            "device_id": "<string>"
        }

    Successful GET Response (HTTP 200):
        {
            "device_id": "<string>",
            "current_state": "<string>",
            "possible_states": ["state1", "state2", ...],
            "requested_state": "<string>" or null,
            "requested_state_start": <int> or null,
            "requested_state_expire": <int> or null
        }

    """

    @app.route("/api/post/state", methods=["POST"])
    def post_state():
        data = request.get_json()
        device_id = data.get('device_id')
        current_state = data.get('current_state')
        possible_states = data.get('possible_states')
        if not (device_id and current_state and possible_states):
            return jsonify({'error': 'Missing required fields'}), 400

        row = state_db.get_state(device_id)
        now = int(time.time())
        requested_state = None
        requested_state_start = None
        requested_state_expire = None

        if row:
            requested_state = row.get('requested_state')
            if requested_state:
                requested_state_start = row.get('requested_state_start')
                requested_state_expire = row.get('requested_state_expire')
                start_ok = (requested_state_start is None) or (requested_state_start == 0) or (now >= requested_state_start)
                expire_ok = (requested_state_expire is None) or (requested_state_expire == 0) or (now <= requested_state_expire)
                requested_state_is_not_current = requested_state != current_state
                if not (start_ok and expire_ok and requested_state_is_not_current):
                    requested_state = None
                    requested_state_start = None
                    requested_state_expire = None

        state_db.set_state(device_id, current_state, possible_states, requested_state, requested_state_start, requested_state_expire)

        return_state = requested_state if requested_state in possible_states else current_state

        return jsonify({
            'state': return_state,
            'debug': {
                'requested_state': requested_state,
                'requested_state_start': requested_state_start,
                'requested_state_expire': requested_state_expire,
                'now': now
            }
        }), 200

    @app.route("/api/get/state", methods=["GET"])
    def get_state():
        device_id = request.args.get('device_id')
        if not device_id:
            return jsonify({'error': 'Missing device_id'}), 400
        row = state_db.get_state(device_id)
        if not row:
            return jsonify({'error': 'Device not found'}), 404
        return jsonify(row)