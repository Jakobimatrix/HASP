import sqlite3
import json
from pathlib import Path
from flask import session

from utilities.password import generateSalt, hashPassword, verifyPassword

DB_FILE = Path(__file__).parent / "users.db"

def getDB():
    return sqlite3.connect(DB_FILE)

def initDB():
    """Initialize the database schema."""
    with getDB() as con:
        con.executescript((Path(__file__).parent / "schema_user.sql").read_text())

def verifyUser(username: str, password: str) -> bool:
    """Check if the given password matches the stored password for the username."""
    with getDB() as con:
        row = con.execute(
            "SELECT salt, password_hash FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        if not row:
            return False
        salt, pw_hash = row
        return verifyPassword(pw_hash, salt, password)

def isCurrentUserInGroup(group: str) -> bool:
    """Check if the currently logged-in user belongs to a specific group."""
    username = session.get("username")
    if not username:
        return False

    with getDB() as con:
        row = con.execute(
            "SELECT user_groups FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        if not row:
            return False

        groups = json.loads(row[0])
        return group in groups

def insertUser(username: str, password: str, groups: list[str]) -> bool:
    """
    Insert a new user into the database with salted password hash.
    Returns True if inserted successfully, False if username already exists.
    """
    salt = generateSalt()
    pw_hash = hashPassword(salt, password)

    try:
        with getDB() as con:
            con.execute(
                "INSERT INTO users (username, password_hash, salt, user_groups) VALUES (?, ?, ?, ?)",
                (username, pw_hash, salt, json.dumps(groups))
            )
        return True
    except sqlite3.IntegrityError:
        # username already exists
        return False

def updateUser(username: str, password: str | None, groups: list[str] | None) -> bool:
    """
    Update user info. If password is not None, it will be updated.
    If groups is not None, groups will be updated.
    Returns True if user exists and updated, False otherwise.
    """
    with getDB() as con:
        row = con.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
        if not row:
            return False  # user does not exist

        updates = []
        params = []

        if password is not None:
            salt = generateSalt()
            pw_hash = hashPassword(salt, password)
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

def deleteUser(username: str) -> bool:
    """Delete a user. Returns True if deleted, False if user does not exist."""
    with getDB() as con:
        cur = con.execute("DELETE FROM users WHERE username = ?", (username,))
        return cur.rowcount > 0

def getUserData(username: str):
    with getDB() as con:
        row = con.execute(
            "SELECT user_groups, username FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if not row:
            return None

        groups_raw, username = row

        try:
            groups = json.loads(groups_raw) if groups_raw else []
        except json.JSONDecodeError:
            groups = []

        return {
            "groups": groups,
            "username": username
        }

def getUserGroups(username: str):
    with getDB() as con:
        row = con.execute(
            "SELECT user_groups FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if not row:
            return None

        groups_raw = row

        try:
            groups = json.loads(groups_raw) if groups_raw else []
        except json.JSONDecodeError:
            groups = []

        return groups

def userExists(username: str):
    with getDB() as con:
        return con.execute(
            "SELECT 1 FROM users WHERE username = ?",
            (username,)
        ).fetchone() is not None