import sqlite3
from pathlib import Path

from utilities.time import Timestamp, getTimeStamp
from db.helper import printDbInfo, enableWalMode

DB_FILE = Path(__file__).parent / "devices.db"

def getDB():
    return sqlite3.connect(DB_FILE)

def initDB():
    with getDB() as con:
        con.executescript((Path(__file__).parent / "schema_devices.sql").read_text())
        printDbInfo(DB_FILE, con)
        enableWalMode(con)

def addNewDevice(device_id, name, info, device):
    timestamp = getTimeStamp()
    if not name:
        name = device_id
    with getDB() as con:
        con.execute(
            "INSERT INTO devices (id, name, info, device, last_seen) VALUES (?, ?, ?, ?, ?)",
            (device_id, name, info, device, timestamp.seconds)
        )

def updateLastSeen(device_id):
    timestamp = getTimeStamp()
    with getDB() as con:
        con.execute(
            "UPDATE devices SET last_seen = ? WHERE id = ?",
            (timestamp.seconds, device_id)
        )

def getAllDevices():
    with getDB() as con:
        return con.execute(
            "SELECT id, name, last_seen FROM devices ORDER BY last_seen DESC"
        ).fetchall()

def deviceExists(device_id):
    with getDB() as con:
        cur = con.execute(
            "SELECT 1 FROM devices WHERE id = ?",
            (device_id,)
        )
        return cur.fetchone() is not None

def getDevice(device_id):
    with getDB() as con:
        row = con.execute(
            "SELECT id, name, info, device, last_seen FROM devices WHERE id = ?",
            (device_id,)
        ).fetchone()
        if row:
            return dict(zip(["id", "name", "info", "device", "last_seen"], row))
        return None

def updateDeviceName(device_id, new_name):
    with getDB() as con:
        con.execute(
            "UPDATE devices SET name = ? WHERE id = ?",
            (new_name, device_id)
        )

def updateDevice(device_id, name, info, device):
    with getDB() as con:
        con.execute(
            "UPDATE devices SET name = ?, info = ?, device = ? WHERE id = ?",
            (name, info, device, device_id)
        )

def removeDevice(device_id):
    with getDB() as con:
        con.execute("DELETE FROM devices WHERE id = ?", (device_id,))
