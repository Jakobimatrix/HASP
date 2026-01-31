import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).parent / "devices.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    with get_connection() as con:
        con.executescript((Path(__file__).parent / "schema_devices.sql").read_text())

def add_device(device_id, name, definition):
    with get_connection() as con:
        con.execute(
            "INSERT INTO devices (id, name, definition, last_seen) VALUES (?, ?, ?, ?)",
            (device_id, name, definition, int(time.time()))
        )

def update_last_seen(device_id):
    with get_connection() as con:
        con.execute(
            "UPDATE devices SET last_seen = ? WHERE id = ?",
            (int(time.time()), device_id)
        )

def get_all_devices():
    with get_connection() as con:
        return con.execute(
            "SELECT id, name, last_seen FROM devices ORDER BY last_seen DESC"
        ).fetchall()

def device_exists(device_id):
    with get_connection() as con:
        cur = con.execute(
            "SELECT 1 FROM devices WHERE id = ?",
            (device_id,)
        )
        return cur.fetchone() is not None
