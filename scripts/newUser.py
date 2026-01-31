#!/usr/bin/env python3
import json
import getpass
from db.user import get_connection, insert_user, init_user_db

def create_user():
    # Ask for username
    username = input("Enter username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return

    # Ask for groups
    groups_input = input("Enter comma-separated groups (e.g., admin,staff): ").strip()
    groups = [g.strip() for g in groups_input.split(",") if g.strip()]
    if not groups:
        print("User must belong to at least one group.")
        return

    # Ask for password twice
    pw1 = getpass.getpass("Enter password: ")
    pw2 = getpass.getpass("Re-enter password: ")

    if pw1 != pw2:
        print("Error: passwords do not match.")
        return

    # Use insert_user from user.py
    success = insert_user(username, pw1, groups)
    if success:
        print(f"User '{username}' created successfully.")
    else:
        print(f"Error: username '{username}' already exists.")


if __name__ == "__main__":
    create_user()
