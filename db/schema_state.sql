CREATE TABLE IF NOT EXISTS state (
    device_id TEXT PRIMARY KEY,
    current_state TEXT NOT NULL,
    requested_state TEXT,
    requested_state_start INTEGER,
    requested_state_expire INTEGER,
    possible_states TEXT NOT NULL -- JSON-encoded list of states
);