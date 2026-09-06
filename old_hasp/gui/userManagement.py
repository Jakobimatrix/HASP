from flask import Blueprint, render_template, request, redirect, url_for
from db.user import insertUser, isCurrentUserInGroup, getDB, updateUser, deleteUser, getUserData
from flask import session
import json

user_bp = Blueprint("user", __name__, template_folder="../templates")


# Add / Add User
@user_bp.route("/add", methods=["GET", "POST"])
def add():
    username = session.get("username")
    if not username or not isCurrentUserInGroup("admin"):
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
            success = insertUser(username_input, password1, groups)
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
    if not username or not isCurrentUserInGroup("admin"):
        return "Access denied.", 403

    users = []
    with getDB() as con:
        rows = con.execute("SELECT username, user_groups FROM users").fetchall()
        for row in rows:
            uname, groups_json = row
            users.append({"username": uname, "groups": json.loads(groups_json)})

    return render_template("userList.html", users=users)


# Delete user
@user_bp.route("/delete/<username>", endpoint="delete")
def deleteUser(username):
    current_user = session.get("username")
    if not current_user or not isCurrentUserInGroup("admin"):
        return "Access denied.", 403

    if username == current_user:
        return "You cannot delete yourself.", 403

    deleteUser(username)
    return redirect(url_for("user.list"))


# Edit user
@user_bp.route("/edit/<username>", methods=["GET", "POST"], endpoint="edit")
def edit(username):
    current_user = session.get("username")
    is_admin = isCurrentUserInGroup("admin")
    if not current_user:
        return "Access denied.", 403

    # Only admin can edit other users; normal users can only edit themselves
    if not is_admin and username != current_user:
        return "Access denied.", 403

    if not userExists(username):
        return f"User '{username}' not found.", 404

    if request.method == "POST":
        password1 = request.form.get("password", "")
        password2 = request.form.get("password2", "")
        # Only allow group changes for admin
        if is_admin:
            groups_input = request.form.get("groups", "").strip()
            new_groups = [g.strip() for g in groups_input.split(",") if g.strip()]
        else:
            new_groups = None

        if password1 or password2:
            if password1 != password2:
                message = "Passwords do not match."
                return render_template("editUser.html", username=username, groups=groups, message=message, is_admin=is_admin)
            else:
                password = password1
        else:
            password = None

        updateUser(username, password, new_groups)
        if is_admin:
            return redirect(url_for("user.list"))
        else:
            return redirect(url_for("index"))

    return render_template("editUser.html", username=username, groups=groups, is_admin=is_admin)


def register(app):
    app.register_blueprint(user_bp, url_prefix="/user")