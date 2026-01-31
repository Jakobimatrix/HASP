# config.py

# please set these variables according to your setup. 
# 1) hange FLASK_SECRET to a different string!
# 2) adjust SSL_INFO to your needs
# 3) look over the other settings and change them if necessary
# 4) save this file

# Flask server settings
HOST = "0.0.0.0"
PORT = 5000
SSL_CERT_FILE = "/etc/flask-certs/flask.pem"
FLASK_SECRET = "CHANGE_THIS_TO_A_DIFFERENT_STRING"
SSL_INFO = "/C=DE/ST=State/L=city/O=organisation/OU=IT-Department/CN=HomeAssistant/emailAddress=your@dress.com"

# Systemd service controlling the Flask app
SERVICE_NAME = "home-assistant-flask.service"


