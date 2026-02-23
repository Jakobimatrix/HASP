import os
from datetime import datetime, timedelta
from flask import Flask
from pathlib import Path
import importlib
import pkgutil
import hashlib
import logging

from config.config import SSL_CERT_FILE, FLASK_SECRET, VERSION, GIT_URL
from db.devices import initDB as init_devices_db
from db.user import initDB as init_user_db
from db.device_data import initDB as init_device_data_db
from db.state import initDB as init_state_db
from db.mqtt import initDB as init_mqtt_db
from mqtt.client import startMqtt


log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

def auto_register(app, package_name):
    package = importlib.import_module(package_name)
    package_path = Path(package.__file__).parent

    for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
        module = importlib.import_module(f"{package_name}.{module_name}")

        if hasattr(module, "register"):
            module.register(app)

def initialize_databases():
    init_devices_db()
    init_user_db()
    init_device_data_db()
    init_state_db()
    init_mqtt_db()


app = Flask(__name__)

# Context processor to inject user and version info into all templates
from flask import session
@app.context_processor
def inject_globals():
    username = session.get("username")
    is_admin = False
    if username:
        try:
            from db.user import isCurrentUserInGroup
            is_admin = isCurrentUserInGroup("admin")
        except Exception:
            is_admin = False
    return dict(
        current_user=username,
        is_admin=is_admin,
        version=VERSION,
        git_url=GIT_URL
    )

now = datetime.now()
shifted = now - timedelta(hours=3)
today_int = int(shifted.strftime("%Y%m%d"))
combined = f"{today_int}-{FLASK_SECRET}".encode()
app.secret_key = hashlib.sha256(combined).digest()

auto_register(app, "api")
auto_register(app, "gui")

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        ssl_context=(SSL_CERT_FILE, SSL_CERT_FILE),
        debug=False,
        use_reloader=False # Avoid double initialization (linux systemd restarts the process)
    )
    initialize_databases()
    startMqtt()
