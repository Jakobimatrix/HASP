-- Store all MQTT topics per device
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    topic_name TEXT NOT NULL,
    has_set BOOL NOT NULL,  -- Whether the device listens to device_id/topic_name/set
    has_state BOOL NOT NULL, -- Whether the device publishes to device_id/topic_name/state
    UNIQUE(device_id, topic_name),
    FOREIGN KEY(device_id) REFERENCES devices(id) ON DELETE CASCADE
);

-- Define data schema per topic (key/value types, min/max, enums)
CREATE TABLE IF NOT EXISTS topic_schema (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    key_name TEXT NOT NULL,
    value_type TEXT NOT NULL,       -- e.g., "int", "float", "string", "bool", "rgb"
    min_value REAL,
    max_value REAL,
    enum_values TEXT,               -- JSON array for dropdowns, optional
    UNIQUE(topic_id),
    FOREIGN KEY(topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

-- Optional: store last payloads or history
CREATE TABLE IF NOT EXISTS topic_payloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    time_seconds INTEGER NOT NULL,
    time_nanoseconds INTEGER NOT NULL,
    payload TEXT NOT NULL,          -- JSON string
    FOREIGN KEY(topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_topics_device
ON topics(device_id);

CREATE INDEX IF NOT EXISTS idx_schema_topic
ON topic_schema(topic_id);

CREATE INDEX IF NOT EXISTS idx_payloads_topic_time
ON topic_payloads(topic_id, time_seconds, time_nanoseconds);