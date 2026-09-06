import sqlite3
import json
from pathlib import Path
from utilities.time import Timestamp, getTimeStamp
from db.helper import printDbInfo, enableWalMode

DB_FILE = Path(__file__).parent / "mqtt.db"
SCHEMA_FILE = Path(__file__).parent / "schema_mqtt.sql"

def getDB():
    con = sqlite3.connect(DB_FILE)
    con.execute("PRAGMA foreign_keys = ON")
    return con

def initDB():
    with getDB() as con:
        con.executescript(SCHEMA_FILE.read_text())
        printDbInfo(DB_FILE, con, SCHEMA_FILE)
        enableWalMode(con)

# ----------------------
TOPICS_TABLE = "topics"
# ----------------------

def addTopic(device_id, topic_name, has_set, has_state):
    topic_id = None
    with getDB() as con:
        con.execute(
            f"INSERT OR IGNORE INTO {TOPICS_TABLE} (device_id, topic_name, has_set, has_state) VALUES (?, ?, ?, ?)",
            (device_id, topic_name, has_set, has_state)
        )
        topic_id = con.execute(f"SELECT last_insert_rowid()").fetchone()[0]
    return topic_id

def getTopicsForDevice(device_id):
    with getDB() as con:
        return con.execute(
            f"SELECT id, topic_name, has_set, has_state FROM {TOPICS_TABLE} WHERE device_id = ? ORDER BY topic_name",
            (device_id,)
        ).fetchall()

def getTopicId(device_id, topic_name):
    with getDB() as con:
        row = con.execute(
            f"SELECT id FROM {TOPICS_TABLE} WHERE device_id = ? AND topic_name = ?",
            (device_id, topic_name)
        ).fetchone()
        if row:
            return row[0]
        return None

def updateDeviceIdForTopics(old_device_id, new_device_id):
    with getDB() as con:
        con.execute(
            f"UPDATE {TOPICS_TABLE} SET device_id = ? WHERE device_id = ?",
            (new_device_id, old_device_id)
        )

def getAllTopics():
    with getDB() as con:
        return con.execute(
            f"SELECT device_id, topic_name, has_set, has_state FROM {TOPICS_TABLE}"
        ).fetchall()

def getTopic(topic_id):
    with getDB() as con:
        row = con.execute(
            f"SELECT id, device_id, topic_name, has_set, has_state FROM {TOPICS_TABLE} WHERE id = ?",
            (topic_id,)
        ).fetchone()
        if row:
            return dict(zip(["id", "device_id", "topic_name", "has_set", "has_state"], row))
        return None

def deleteTopic(topic_id):
    with getDB() as con:
        con.execute(f"DELETE FROM {TOPICS_TABLE} WHERE id = ?", (topic_id,))

# ----------------------
TOPICS_SCHEMA_TABLE = "topic_schema"
# ----------------------

def addTopicSchema(topic_id, key_name, value_type, min_value=None, max_value=None, enum_values=None):
    if enum_values is not None:
        enum_values = json.dumps(enum_values)
    with getDB() as con:
        con.execute(
            f"""
            INSERT INTO {TOPICS_SCHEMA_TABLE} (topic_id, key_name, value_type, min_value, max_value, enum_values)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (topic_id, key_name, value_type, min_value, max_value, enum_values)
        )

def getTopicSchema(topic_id):
    return getTopicSchemaActiveConnection(topic_id, getDB() )

def getTopicSchemaActiveConnection(topic_id, db_connection):
    with db_connection as con:
        rows = con.execute(
            f"SELECT id, key_name, value_type, min_value, max_value, enum_values FROM {TOPICS_SCHEMA_TABLE} WHERE topic_id = ?",
            (topic_id,)
        ).fetchall()
        return [dict(zip(["id", "key_name", "value_type", "min_value", "max_value", "enum_values"], r)) for r in rows]


def getAllTopicsForDevice(device_id):
    dbConnection = getDB()
    with dbConnection as con:
        topic_rows = con.execute(
            f"SELECT id, topic_name FROM {TOPICS_TABLE} WHERE device_id = ? ORDER BY topic_name",
            (device_id,)
        ).fetchall()

    topics = []
    for topic_id, name in topic_rows:
        keys = getTopicSchemaActiveConnection(topic_id, dbConnection)
        topic_info = getTopic(topic_id)
        if not topic_info:
            print(f"Error: Topic with id {topic_id} fount in {TOPICS_SCHEMA_TABLE} but not in {TOPICS_TABLE}. This should not happen.")
            continue

        # Normalize enum_values from JSON string → list
        for k in keys:
            if k["enum_values"]:
                try:
                    k["enum_values"] = json.loads(k["enum_values"])
                except Exception:
                    k["enum_values"] = []

        topics.append({
            "id": topic_id,
            "name": name,
            "keys": keys,
            "has_set": topic_info["has_set"],
            "has_state": topic_info["has_state"]
        })

    return topics

def deleteTopicSchema(topic_id):
    with getDB() as con:
        con.execute("DELETE FROM topic_schema WHERE id = ?", (topic_id,))

def deleteTopicSchemaForTopic(topic_id):
    with getDB() as con:
        con.execute("DELETE FROM topic_schema WHERE topic_id = ?", (topic_id,))

# ----------------------
TOPICS_TABLE_PAYLOADS = "topic_payloads"
# ----------------------

def addTopicPayload(topic_id, payload):
    timestamp = getTimeStamp()
    with getDB() as con:
        con.execute(
            f"INSERT INTO {TOPICS_TABLE_PAYLOADS} (topic_id, time_seconds, time_nanoseconds, payload) VALUES (?, ?, ?, ?)",
            (topic_id, timestamp.seconds, timestamp.nanoseconds, json.dumps(payload))
        )

def getLatestPayload(topic_id):
    with getDB() as con:
        row = con.execute(
            f"SELECT time_seconds, time_nanoseconds, payload FROM {TOPICS_TABLE_PAYLOADS} WHERE topic_id = ? ORDER BY time_seconds DESC, time_nanoseconds DESC LIMIT 1",
            (topic_id,)
        ).fetchone()
        if row:
            return dict(zip(["time_seconds", "time_nanoseconds", "payload"], row))
        return None

def getPayloadHistory(topic_id, limit=100):
    with getDB() as con:
        rows = con.execute(
            f"SELECT time_seconds, time_nanoseconds, payload FROM {TOPICS_TABLE_PAYLOADS} WHERE topic_id = ? ORDER BY time_seconds DESC, time_nanoseconds DESC LIMIT ?",
            (topic_id, limit)
        ).fetchall()
        return [dict(zip(["time_seconds", "time_nanoseconds", "payload"], r)) for r in rows]

def deletePayloads(topic_id):
    with getDB() as con:
        con.execute(f"DELETE FROM {TOPICS_TABLE_PAYLOADS} WHERE topic_id = ?", (topic_id,))

