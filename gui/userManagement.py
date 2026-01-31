from flask import Blueprint, render_template, request, redirect, url_for
from db.user import insert_user, is_current_user_in_group, get_connection, update_user, delete_user
from flask import session
import json

user_bp = Blueprint("user", __name__, template_folder="../templates")


# Add / Add User
@user_bp.route("/add", methods=["GET", "POST"])
def add():
    username = session.get("username")
    if not username or not is_current_user_in_group("admin"):
        return "Access denied.", 403

    if request.method == "POST":
        username_input = request.form.get("username", "").strip()
        groups_input = request.form.get("groups", "").strip()
        password1 = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        groups = [g.strip() for g in groups_input.split(",") if g.strip()]

        if not username_input or not groups:
            message = "Username and groups are required."
        elif password1 != password2:
            message = "Passwords do not match."
        else:
            success = insert_user(username_input, password1, groups)
            if success:
                return redirect(url_for("user.list"))
            else:
                message = f"Username '{username_input}' already exists."

        return render_template("addUser.html", message=message, success=False)

    return render_template("addUser.html")


# User list
@user_bp.route("/list", endpoint="list")
def listAll():
    username = session.get("username")
    if not username or not is_current_user_in_group("admin"):
        return "Access denied.", 403

    users = []
    with get_connection() as con:
        rows = con.execute("SELECT username, user_groups FROM users").fetchall()
        for row in rows:
            uname, groups_json = row
            users.append({"username": uname, "groups": json.loads(groups_json)})

    return render_template("userList.html", users=users)


# Delete user
@user_bp.route("/delete/<username>", endpoint="delete")
def deleteUser(username):
    current_user = session.get("username")
    if not current_user or not is_current_user_in_group("admin"):
        return "Access denied.", 403

    if username == current_user:
        return "You cannot delete yourself.", 403

    delete_user(username)
    return redirect(url_for("user.list"))


# Edit user
@user_bp.route("/edit/<username>", methods=["GET", "POST"], endpoint="edit")
def edit(username):
    current_user = session.get("username")
    if not current_user or not is_current_user_in_group("admin"):
        return "Access denied.", 403

    # Get current user data
    with get_connection() as con:
        row = con.execute("SELECT user_groups FROM users WHERE username = ?", (username,)).fetchone()
        if not row:
            return f"User '{username}' not found.", 404
        groups = json.loads(row[0])

    if request.method == "POST":
        password1 = request.form.get("password", "")
        password2 = request.form.get("password2", "")
        groups_input = request.form.get("groups", "").strip()
        new_groups = [g.strip() for g in groups_input.split(",") if g.strip()]

        if password1 or password2:
            if password1 != password2:
                message = "Passwords do not match."
                return render_template("editUser.html", username=username, groups=new_groups, message=message)
            else:
                password = password1
        else:
            password = None

        update_user(username, password, new_groups)
        return redirect(url_for("user.list"))

    return render_template("editUser.html", username=username, groups=groups)


def register(app):
    app.register_blueprint(user_bp, url_prefix="/user")