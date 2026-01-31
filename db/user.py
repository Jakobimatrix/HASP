import sqlite3
import json
from pathlib import Path
from flask import session

from utilities import password_utils

DB_FILE = Path(__file__).parent / "users.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_user_db():
    """Initialize the database schema."""
    with get_connection() as con:
        con.executescript((Path(__file__).parent / "user_schema.sql").read_text())

def verify_user(username: str, password: str) -> bool:
    """Check if the given password matches the stored password for the username."""
    with get_connection() as con:
        row = con.execute(
            "SELECT salt, password_hash FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        if not row:
            return False
        salt, pw_hash = row
        return password_utils.verify_password(pw_hash, salt, password)

def is_current_user_in_group(group: str) -> bool:
    """Check if the currently logged-in user belongs to a specific group."""
    username = session.get("username")
    if not username:
        return False

    with get_connection() as con:
        row = con.execute(
            "SELECT user_groups FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        if not row:
            return False

        groups = json.loads(row[0])
        return group in groups

def insert_user(username: str, password: str, groups: list[str]) -> bool:
    """
    Insert a new user into the database with salted password hash.
    Returns True if inserted successfully, False if username already exists.
    """
    salt = password_utils.generate_salt()
    pw_hash = password_utils.hash_password(salt, password)

    try:
        with get_connection() as con:
            con.execute(
                "INSERT INTO users (username, password_hash, salt, user_groups) VALUES (?, ?, ?, ?)",
                (username, pw_hash, salt, json.dumps(groups))
            )
        return True
    except sqlite3.IntegrityError:
        # username already exists
        return False

def update_user(username: str, password: str | None, groups: list[str] | None) -> bool:
    """
    Update user info. If password is not None, it will be updated.
    If groups is not None, groups will be updated.
    Returns True if user exists and updated, False otherwise.
    """
    with get_connection() as con:
        row = con.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
        if not row:
            return False  # user does not exist

        updates = []
        params = []

        if password is not None:
            salt = password_utils.generate_salt()
            pw_hash = password_utils.hash_password(salt, password)
            updates.append("password_hash = ?, salt = ?")
            params.extend([pw_hash, salt])

        if groups is not None:
            updates.append("user_groups = ?")
            params.append(json.dumps(groups))

        if updates:
            sql = f"UPDATE users SET {', '.join(updates)} WHERE username = ?"
            params.append(username)
            con.execute(sql, params)

        return True

def delete_user(username: str) -> bool:
    """Delete a user. Returns True if deleted, False if user does not exist."""
    with get_connection() as con:
        cur = con.execute("DELETE FROM users WHERE username = ?", (username,))
        return cur.rowcount > 0
