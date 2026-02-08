from flask import request, render_template, session, redirect, url_for
from db.user import verifyUser

def register(app):

    @app.route("/login", methods=["GET", "POST"], endpoint="login")
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            if verifyUser(username, password):
                session["username"] = username
                return redirect(url_for("index"))
            else:
                return render_template("login.html", error="Invalid credentials")

        return render_template("login.html")
