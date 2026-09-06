from flask import Blueprint, render_template, session
from db.user import isCurrentUserInGroup


def register(app):

    @app.route("/index", endpoint="index")
    def index():
        username = session.get("username")
        logged_in = username is not None
        is_admin = logged_in and isCurrentUserInGroup("admin")
        return render_template("index.html", logged_in=logged_in, is_admin=is_admin)