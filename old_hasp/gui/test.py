from flask import render_template

def register(app):

    @app.route("/test", endpoint="test")
    def test():
        return render_template("test.html")
