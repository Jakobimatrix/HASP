import sqlite3
import json
from pathlib import Path

DB_FILE = Path(__file__).parent / "state.db"

def getDB():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def initDB():
    """Initialize the database schema."""
    with getDB() as con:
        con.executescript((Path(__file__).parent / "schema_state.sql").read_text())

def getDeviceState(device_id):
    conn = getDB()
    cur = conn.execute('SELECT * FROM state WHERE device_id = ?', (device_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        result = dict(row)
        if result['possible_states']:
            result['possible_states'] = json.loads(result['possible_states'])
        return result
    return None

def setDeviceState(device_id, current_state, possible_states, requested_state, requested_state_start, requested_state_expire):
    conn = getDB()
    possible_states_json = json.dumps(possible_states)
    conn.execute('''INSERT INTO state (device_id, current_state, possible_states, requested_state, requested_state_start, requested_state_expire)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(device_id) DO UPDATE SET
                        current_state=excluded.current_state,
                        possible_states=excluded.possible_states,
                        requested_state=excluded.requested_state,
                        requested_state_start=excluded.requested_state_start,
                        requested_state_expire=excluded.requested_state_expire''',
                 (device_id, current_state, possible_states_json, requested_state, requested_state_start, requested_state_expire))
    conn.commit()
    conn.close()

def updateRequestedDeviceState(device_id, requested_state, requested_state_start=None, requested_state_expire=None):
    conn = getDB()
    conn.execute('''UPDATE state SET requested_state=?, requested_state_start=?, requested_state_expire=? WHERE device_id=?''',
                 (requested_state, requested_state_start, requested_state_expire, device_id))
    conn.commit()
    conn.close()

def deleteDeviceState(device_id):
    with getDB() as con:
        con.execute("DELETE FROM state WHERE device_id = ?", (device_id,))
