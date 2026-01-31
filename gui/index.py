from flask import Blueprint, render_template, session
from db.user import is_current_user_in_group


def register(app):

    @app.route("/index", endpoint="index")
    def index():
        username = session.get("username")
        logged_in = username is not None
        is_admin = logged_in and is_current_user_in_group("admin")
        return render_template("index.html", logged_in=logged_in, is_admin=is_admin)