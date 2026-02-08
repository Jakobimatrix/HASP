CREATE TABLE IF NOT EXISTS devices (
    id TEXT PRIMARY KEY,
    name TEXT,
    info TEXT,
    device TEXT,
    last_seen INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_devices_id
ON devices(id);
