import os
import sqlite3


def print_db_info(DB_FILE, connection) -> None:
    print("=== DATABASE FILE INFO ===")
    print(f"Path: {DB_FILE.resolve()}")

    if not DB_FILE.exists():
        print("Database file does not exist.")
        return

    size_bytes = DB_FILE.stat().st_size
    print(f"Size: {size_bytes} bytes ({size_bytes / 1024:.2f} KiB)")

    cur = connection.cursor()

    print("\n=== SQLITE INFO ===")
    cur.execute("SELECT sqlite_version();")
    print(f"SQLite version: {cur.fetchone()[0]}")

    print("\n=== PRAGMA DATABASE LIST ===")
    for row in cur.execute("PRAGMA database_list;"):
        print(row)

    print("\n=== PRAGMA SETTINGS ===")
    for pragma in [
        "journal_mode",
        "synchronous",
        "page_size",
        "page_count",
        "freelist_count",
        "auto_vacuum",
    ]:
        cur.execute(f"PRAGMA {pragma};")
        print(f"{pragma}: {cur.fetchone()[0]}")

    print("\n=== TABLES ===")
    tables = list(
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        )
    )

    if not tables:
        print("No tables found.")
        return

    for (table_name,) in tables:
        print(f"\n--- TABLE: {table_name} ---")

        # Schema
        cur.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?;",
            (table_name,),
        )
        print("Schema:")
        print(cur.fetchone()[0])

        # Columns
        print("\nColumns:")
        for col in cur.execute(f"PRAGMA table_info({table_name});"):
            print(col)

        # Indexes
        print("\nIndexes:")
        indexes = list(cur.execute(f"PRAGMA index_list({table_name});"))
        if not indexes:
            print("  (none)")
        else:
            for idx in indexes:
                print(" ", idx)

        # Foreign Keys
        print("\nForeign Keys:")
        fks = list(cur.execute(f"PRAGMA foreign_key_list({table_name});"))
        if not fks:
            print("  (none)")
        else:
            for fk in fks:
                print(" ", fk)

        # Row count
        cur.execute(f"SELECT COUNT(*) FROM {table_name};")
        print(f"\nRow count: {cur.fetchone()[0]}")

        print("\n=== INTEGRITY CHECK ===")
        cur.execute("PRAGMA integrity_check;")
        print(cur.fetchone()[0])