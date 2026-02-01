import sqlite3
from pathlib import Path
from typing import Any, Iterable, Optional, Tuple

from utilities.time_utils import Timestamp, get_timestamp


DB_FILE = Path(__file__).parent / "device_data.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    with get_connection() as con:
        con.executescript((Path(__file__).parent / "schema_device_data.sql").read_text())

def insert_measurement(
    device_id: str,
    ts_sec: int,
    ts_nsec: int,
    key: str,
    value: Any,
    report_id: Optional[str] = None,
):
    value_num = value_int = value_text = value_bool = None

    if isinstance(value, bool):
        value_bool = int(value)
    elif isinstance(value, int):
        value_int = value
    elif isinstance(value, float):
        value_num = value
    else:
        value_text = str(value)

    with get_connection() as con:
        con.execute(
            """
            INSERT INTO measurements
            (device_id, ts_sec, ts_nsec, key,
             value_num, value_int, value_text, value_bool,
             report_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                device_id, ts_sec, ts_nsec, key,
                value_num, value_int, value_text, value_bool,
                report_id,
            ),
        )

def insert_measurements(
    rows: Iterable[
        Tuple[str, int, int, str, Any, Optional[str]]
    ]
):
    prepared = []

    for device_id, ts_sec, ts_nsec, key, value, report_id in rows:
        value_num = value_int = value_text = value_bool = None

        if isinstance(value, bool):
            value_bool = int(value)
        elif isinstance(value, int):
            value_int = value
        elif isinstance(value, float):
            value_num = value
        else:
            value_text = str(value)

        prepared.append(
            (
                device_id, ts_sec, ts_nsec, key,
                value_num, value_int, value_text, value_bool,
                report_id,
            )
        )

    with get_connection() as con:
        con.executemany(
            """
            INSERT INTO measurements
            (device_id, ts_sec, ts_nsec, key,
             value_num, value_int, value_text, value_bool,
             report_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            prepared,
        )

def get_all_keys(device_ids: Optional[list[str]] = None):
    with get_connection() as con:
        if device_ids:
            placeholders = ",".join("?" * len(device_ids))
            rows = con.execute(
                f"""
                SELECT DISTINCT key
                FROM measurements
                WHERE device_id IN ({placeholders})
                ORDER BY key
                """,
                device_ids,
            )
        else:
            rows = con.execute(
                "SELECT DISTINCT key FROM measurements ORDER BY key"
            )
        return [r[0] for r in rows]

def get_time_series(device_id: str, key: str):
    with get_connection() as con:
        return con.execute(
            """
            SELECT ts_sec, ts_nsec,
                   COALESCE(value_num, value_int, value_text, value_bool) AS value
            FROM measurements
            WHERE device_id = ?
              AND key = ?
            ORDER BY ts_sec, ts_nsec
            """,
            (device_id, key),
        ).fetchall()

def get_xy_series(device_id: str, x_key: str, y_key: str):
    with get_connection() as con:
        return con.execute(
            """
            SELECT
                x.value_num AS x,
                y.value_num AS y
            FROM measurements x
            JOIN measurements y
              ON x.device_id = y.device_id
             AND x.report_id = y.report_id
            WHERE x.device_id = ?
              AND x.key = ?
              AND y.key = ?
              AND x.report_id IS NOT NULL
            """,
            (device_id, x_key, y_key),
        ).fetchall()