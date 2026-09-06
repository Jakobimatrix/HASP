import os
import sqlite3
from flask import current_app
import re

def enableWalMode(connection) -> None:
    cur = connection.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    mode = cur.fetchone()[0]
    print(f"Journal mode set to: {mode}")

    cur.execute("PRAGMA synchronous=NORMAL;")
    print("Synchronous set to NORMAL")

def printDbInfo(DB_FILE, connection, SCHEMA_FILE) -> None:
    if not current_app.debug:
        return

    def info(msg): print(f"[INFO] {msg}")
    def warn(msg): print(f"[WARNING] {msg}")
    def error(msg): print(f"[ERROR] {msg}")

    print("\n========== DATABASE HEALTH CHECK ==========\n")

    if not DB_FILE.exists():
        error("Database file does not exist.")
        return

    size_bytes = DB_FILE.stat().st_size
    info(f"Path: {DB_FILE.resolve()}")
    info(f"Size: {size_bytes} bytes ({size_bytes / 1024:.2f} KiB)")

    cur = connection.cursor()

    # -------------------------------------------------
    # SQLITE VERSION
    # -------------------------------------------------
    cur.execute("SELECT sqlite_version();")
    sqlite_version = cur.fetchone()[0]
    info(f"SQLite version: {sqlite_version}")

    # -------------------------------------------------
    # PRAGMA SETTINGS
    # -------------------------------------------------
    cur.execute("PRAGMA journal_mode;")
    journal_mode = cur.fetchone()[0]
    info(f"journal_mode: {journal_mode}")
    if journal_mode.lower() != "wal":
        warn("WAL mode not enabled (recommended for write-heavy workloads).")

    cur.execute("PRAGMA synchronous;")
    synchronous = cur.fetchone()[0]
    info(f"synchronous: {synchronous}")
    if synchronous == 2:
        warn("synchronous=FULL (safe but slower).")
    if synchronous == 0:
        error("synchronous=OFF (risk of corruption).")

    cur.execute("PRAGMA foreign_keys;")
    fk_enabled = cur.fetchone()[0]
    info(f"foreign_keys: {fk_enabled}")
    if fk_enabled == 0:
        warn("Foreign key enforcement is disabled.")

    cur.execute("PRAGMA page_size;")
    page_size = cur.fetchone()[0]

    cur.execute("PRAGMA page_count;")
    page_count = cur.fetchone()[0]

    cur.execute("PRAGMA freelist_count;")
    freelist = cur.fetchone()[0]

    total_size_calc = page_size * page_count
    info(f"page_size: {page_size}")
    info(f"page_count: {page_count}")
    info(f"freelist_count: {freelist}")

    if freelist > page_count * 0.2:
        warn("More than 20% pages unused. Consider VACUUM.")

    # -------------------------------------------------
    # TABLE VALIDATION
    # -------------------------------------------------
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    actual_tables = {row[0] for row in cur.fetchall()}

    expected_schema_sql = SCHEMA_FILE.read_text()
    expected_tables = set(
        re.findall(r"CREATE TABLE IF NOT EXISTS (\w+)", expected_schema_sql)
    )

    missing_tables = expected_tables - actual_tables
    extra_tables = actual_tables - expected_tables - {"sqlite_sequence"}

    if missing_tables:
        error(f"Missing tables: {missing_tables}")

    if extra_tables:
        warn(f"Unexpected tables found: {extra_tables}")

    # -------------------------------------------------
    # PER TABLE CHECK
    # -------------------------------------------------
    for table in sorted(actual_tables):
        print(f"\n--- TABLE: {table} ---")

        cur.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?;",
            (table,),
        )
        schema_row = cur.fetchone()

        if not schema_row or not schema_row[0]:
            error("Missing schema definition.")
            continue

        info("Schema present.")

        # Column check
        cur.execute(f"PRAGMA table_info({table});")
        columns = cur.fetchall()
        if not columns:
            error("No columns found.")
        else:
            info(f"{len(columns)} columns defined.")

        # Index check
        cur.execute(f"PRAGMA index_list({table});")
        indexes = cur.fetchall()

        if not indexes:
            warn("No indexes found.")

        # Redundant index detection
        index_columns_map = {}
        for idx in indexes:
            idx_name = idx[1]
            cur.execute(f"PRAGMA index_info({idx_name});")
            cols = tuple(row[2] for row in cur.fetchall())
            index_columns_map[idx_name] = cols

        # detect duplicate index column definitions
        seen = {}
        for name, cols in index_columns_map.items():
            if cols in seen:
                warn(f"Redundant index: {name} duplicates {seen[cols]}")
            else:
                seen[cols] = name

        # Row count
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            row_count = cur.fetchone()[0]
            info(f"Row count: {row_count}")
        except Exception as e:
            error(f"Row count failed: {e}")

    # -------------------------------------------------
    # INTEGRITY CHECK
    # -------------------------------------------------
    cur.execute("PRAGMA integrity_check;")
    integrity = cur.fetchone()[0]
    if integrity != "ok":
        error(f"Integrity check failed: {integrity}")
    else:
        info("Integrity check OK")

    # -------------------------------------------------
    # FINAL SIZE ANALYSIS
    # -------------------------------------------------
    if size_bytes > 100 * 1024 * 1024:
        warn("Database larger than 100MB. Consider archiving strategy.")

    print("\n========== DATABASE CHECK COMPLETE ==========\n")