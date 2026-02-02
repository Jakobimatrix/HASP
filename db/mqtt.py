import sqlite3
from pathlib import Path
from utilities.time_utils import Timestamp, get_timestamp

DB_FILE = Path(__file__).parent / "mqtt.db"
SCHEMA_FILE = Path(__file__).parent / "schema_mqtt.sql"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    with get_connection() as con:
        con.executescript(SCHEMA_FILE.read_text())

# ----------------------
TOPICS_TABLE = "topics"
# ----------------------

def add_topic(device_id, topic_name):
    with get_connection() as con:
        con.execute(
            f"INSERT OR IGNORE INTO {TOPICS_TABLE} (device_id, topic_name) VALUES (?, ?)",
            (device_id, topic_name)
        )

def get_topics_for_device(device_id):
    with get_connection() as con:
        return con.execute(
            f"SELECT id, topic_name FROM {TOPICS_TABLE} WHERE device_id = ? ORDER BY topic_name",
            (device_id,)
        ).fetchall()

def get_topic(topic_id):
    with get_connection() as con:
        row = con.execute(
            f"SELECT id, device_id, topic_name FROM {TOPICS_TABLE} WHERE id = ?",
            (topic_id,)
        ).fetchone()
        if row:
            return dict(zip(["id", "device_id", "topic_name"], row))
        return None

def delete_topic(topic_id):
    with get_connection() as con:
        con.execute(f"DELETE FROM {TOPICS_TABLE} WHERE id = ?", (topic_id,))
def update_topic_name(topic_id, new_name):
    with get_connection() as con:
        con.execute(
            f"UPDATE {TOPICS_TABLE} SET topic_name = ? WHERE id = ?",
            (new_name, topic_id)
        )

# ----------------------
TOPICS_SCHEMA_TABLE = "topic_schema"
# ----------------------

def add_topic_schema(topic_id, key_name, value_type, min_value=None, max_value=None, enum_values=None):
    with get_connection() as con:
        con.execute(
            f"""
            INSERT INTO {TOPICS_SCHEMA_TABLE} (topic_id, key_name, value_type, min_value, max_value, enum_values)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (topic_id, key_name, value_type, min_value, max_value, enum_values)
        )

def get_topic_schema(topic_id):
    with get_connection() as con:
        rows = con.execute(
            f"SELECT id, key_name, value_type, min_value, max_value, enum_values FROM {TOPICS_SCHEMA_TABLE} WHERE topic_id = ?",
            (topic_id,)
        ).fetchall()
        return [dict(zip(["id", "key_name", "value_type", "min_value", "max_value", "enum_values"], r)) for r in rows]

TOPICS_TABLE = "topics"

def get_all_topics_for_device(device_id):
    with get_connection() as con:
        topic_rows = con.execute(
            f"SELECT id, name FROM {TOPICS_TABLE} WHERE device_id = ? ORDER BY name",
            (device_id,)
        ).fetchall()

    topics = []
    for topic_id, name in topic_rows:
        keys = get_topic_schema(topic_id)

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
            "keys": keys
        })

    return topics

def update_topic_schema(schema_id, key_name=None, value_type=None, min_value=None, max_value=None, enum_values=None):
    updates = []
    params = []
    if key_name is not None:
        updates.append("key_name = ?")
        params.append(key_name)
    if value_type is not None:
        updates.append("value_type = ?")
        params.append(value_type)
    if min_value is not None:
        updates.append("min_value = ?")
        params.append(min_value)
    if max_value is not None:
        updates.append("max_value = ?")
        params.append(max_value)
    if enum_values is not None:
        updates.append("enum_values = ?")
        params.append(enum_values)
    if updates:
        params.append(schema_id)
        with get_connection() as con:
            con.execute(f"UPDATE topic_schema SET {', '.join(updates)} WHERE id = ?", params)

def delete_topic_schema(schema_id):
    with get_connection() as con:
        con.execute("DELETE FROM topic_schema WHERE id = ?", (schema_id,))

def delete_topic_schema_for_topic(topic_id):
    schemas = get_topic_schema(topic_id)
    for schema in schemas:
        delete_topic_schema(schema["id"])

# ----------------------
TOPICS_TABLE_PAYLOADS = "topic_payloads"
# ----------------------

def add_topic_payload(topic_id, payload):
    timestamp = get_timestamp()
    with get_connection() as con:
        con.execute(
            f"INSERT INTO {TOPICS_TABLE_PAYLOADS} (topic_id, time_seconds, time_nanoseconds, payload) VALUES (?, ?, ?, ?)",
            (topic_id, timestamp.seconds, timestamp.nanoseconds, payload)
        )

def get_latest_payload(topic_id):
    with get_connection() as con:
        row = con.execute(
            f"SELECT time_seconds, time_nanoseconds, payload FROM {TOPICS_TABLE_PAYLOADS} WHERE topic_id = ? ORDER BY time_seconds DESC, time_nanoseconds DESC LIMIT 1",
            (topic_id,)
        ).fetchone()
        if row:
            return dict(zip(["time_seconds", "time_nanoseconds", "payload"], row))
        return None

def get_payload_history(topic_id, limit=100):
    with get_connection() as con:
        rows = con.execute(
            f"SELECT time_seconds, time_nanoseconds, payload FROM {TOPICS_TABLE_PAYLOADS} WHERE topic_id = ? ORDER BY time_seconds DESC, time_nanoseconds DESC LIMIT ?",
            (topic_id, limit)
        ).fetchall()
        return [dict(zip(["time_seconds", "time_nanoseconds", "payload"], r)) for r in rows]

def delete_payloads(topic_id):
    with get_connection() as con:
        con.execute(f"DELETE FROM {TOPICS_TABLE_PAYLOADS} WHERE topic_id = ?", (topic_id,))

