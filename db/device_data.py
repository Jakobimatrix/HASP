import sqlite3
from pathlib import Path
from typing import Any, Iterable, Optional, Tuple

from utilities.time import Timestamp, getTimeStamp
from db.helper import printDbInfo, enableWalMode


DB_FILE = Path(__file__).parent / "device_data.db"
SCHEMA_FILE = Path(__file__).parent / "schema_device_data.sql"

def getDB():
    return sqlite3.connect(DB_FILE)

def initDB():
    with getDB() as con:
        con.executescript(SCHEMA_FILE.read_text())
        printDbInfo(DB_FILE, con, SCHEMA_FILE)  
        enableWalMode(con)      

def insertMeasurement(
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

    with getDB() as con:
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

def insertMeasurements(
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

    with getDB() as con:
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

def getAllKeys(device_ids: Optional[list[str]] = None):
    with getDB() as con:
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

def getAllReportIds(device_ids: Optional[list[str]] = None):
    with getDB() as con:
        if device_ids:
            placeholders = ",".join("?" * len(device_ids))
            rows = con.execute(
                f"""
                SELECT DISTINCT report_id
                FROM measurements
                WHERE device_id IN ({placeholders})
                  AND report_id IS NOT NULL
                  AND report_id != ''
                ORDER BY report_id
                """,
                device_ids,
            )
        else:
            rows = con.execute(
                """
                SELECT DISTINCT report_id FROM measurements
                WHERE report_id IS NOT NULL AND report_id != ''
                ORDER BY report_id
                """
            )
        return [r[0] for r in rows]

def getTimeSeries(device_id: str, key: str):
    with getDB() as con:
        return con.execute(
            """
            SELECT ts_sec, ts_nsec,
                   COALESCE(value_num, value_int, value_text, value_bool) AS value,
                   report_id
            FROM measurements
            WHERE device_id = ?
              AND key = ?
            ORDER BY ts_sec, ts_nsec
            """,
            (device_id, key),
        ).fetchall()

def getXYSeries(device_id: str, x_key: str, y_key: str):
    with getDB() as con:
        return con.execute(
            """
            SELECT
                x.ts_sec,
                x.ts_nsec,
                COALESCE(x.value_num, x.value_int, x.value_text, x.value_bool) AS x,
                COALESCE(y.value_num, y.value_int, y.value_text, y.value_bool) AS y
            FROM measurements x
            JOIN measurements y
            ON x.device_id = y.device_id
            AND x.ts_sec = y.ts_sec
            AND x.ts_nsec = y.ts_nsec
            WHERE x.device_id = ?
            AND x.key = ?
            AND y.key = ?
            ORDER BY x.ts_sec, x.ts_nsec
            """,
            (device_id, x_key, y_key),
        ).fetchall()

def getTimeSeriesViaReportId(report_id: str, device_id: str = None):  
    with getDB() as con:
        if device_id is None:
            return con.execute(
                """
                SELECT ts_sec, ts_nsec, device_id, key,
                       COALESCE(value_num, value_int, value_text, value_bool) AS value,
                       report_id
                FROM measurements
                WHERE report_id = ?
                ORDER BY ts_sec, ts_nsec
                """,
                (report_id,),
            ).fetchall()
        return con.execute(
            """
            SELECT ts_sec, ts_nsec, key,
                   COALESCE(value_num, value_int, value_text, value_bool) AS value,
                   report_id
            FROM measurements
            WHERE report_id = ?
              AND device_id = ?
            ORDER BY ts_sec, ts_nsec
            """,
            (report_id, device_id),
        ).fetchall()

def getAllDataWithAReportId():
    with getDB() as con:
        return con.execute(
            """
            SELECT ts_sec, ts_nsec, device_id, key,
                COALESCE(value_num, value_int, value_text, value_bool) AS value,
                report_id
            FROM measurements
            WHERE report_id IS NOT NULL AND report_id != ''
            ORDER BY ts_sec, ts_nsec
            """
        ).fetchall()

def removeDeviceData(device_id):
    with getDB() as con:
        con.execute("DELETE FROM measurements WHERE device_id = ?", (device_id,))

def countDeviceData(device_id):
    with getDB() as con:
        row = con.execute("SELECT COUNT(*) FROM measurements WHERE device_id = ?", (device_id,)).fetchone()
        return row[0] if row else 0

def updateDeviceId(old_id, new_id):
    with getDB() as con:
        con.execute("UPDATE measurements SET device_id = ? WHERE device_id = ?", (new_id, old_id))
