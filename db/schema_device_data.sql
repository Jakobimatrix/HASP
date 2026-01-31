CREATE TABLE measurements (
    device_id   TEXT    NOT NULL,
    ts_sec      INTEGER NOT NULL,
    ts_nsec     INTEGER NOT NULL,
    key         TEXT    NOT NULL,

    value_num   REAL,
    value_int   INTEGER,
    value_text  TEXT,
    value_bool  INTEGER,

    report_id   TEXT,

    PRIMARY KEY (device_id, ts_sec, ts_nsec, key)
);
