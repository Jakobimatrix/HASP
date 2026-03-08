from config.config import SSL_CERT_FILE


workers = 2
bind = "0.0.0.0:5000"
timeout = 120
max_requests = 1000
max_requests_jitter = 100

certfile = SSL_CERT_FILE
keyfile = SSL_CERT_FILE


def on_starting(server):
    from mqtt.client import startMqtt
    from server import initialize_databases
    
    initialize_databases()

    startMqtt()