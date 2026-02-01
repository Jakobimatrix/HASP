import os
from datetime import datetime, timedelta
from flask import Flask
from pathlib import Path
import importlib
import pkgutil
import hashlib

from config.config import SSL_CERT_FILE
from config.config import FLASK_SECRET
from db.devices import init_db as init_devices_db
from db.user import init_db as init_user_db
from db.device_data import init_db as init_device_data_db
from db.state import init_db as init_state_db

def auto_register(app, package_name):
    package = importlib.import_module(package_name)
    package_path = Path(package.__file__).parent

    for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
        module = importlib.import_module(f"{package_name}.{module_name}")

        if hasattr(module, "register"):
            module.register(app)

init_devices_db()
init_user_db()
init_device_data_db()
init_state_db()

app = Flask(__name__)

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
        ssl_context=(SSL_CERT_FILE, SSL_CERT_FILE)
    )
