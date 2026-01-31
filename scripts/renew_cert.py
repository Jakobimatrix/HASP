#!/usr/bin/env python3
import sys
from pathlib import Path

# Add project root to PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import subprocess
from datetime import date
from config.config import SSL_CERT_FILE
from config.config import SSL_INFO

CERT_FILE = Path(SSL_CERT_FILE)
DAYS = 365

# Ensure directory exists
CERT_FILE.parent.mkdir(parents=True, exist_ok=True)

# Backup old cert if exists
if CERT_FILE.exists():
    backup_file = CERT_FILE.with_name(f"{CERT_FILE.name}.bak-{date.today()}")
    CERT_FILE.replace(backup_file)
    print(f"Backed up old cert to {backup_file}")

# Generate new self-signed certificate
subprocess.run([
    "openssl", "req", "-new", "-x509",
    "-keyout", str(CERT_FILE),
    "-out", str(CERT_FILE),
    "-days", str(DAYS),
    "-nodes",
    "-subj", str(SSL_INFO)
], check=True)

# Set permissions
CERT_FILE.chmod(0o400)
subprocess.run(["chown", "root:root", str(CERT_FILE)], check=True)

print(f"Certificate generated at {CERT_FILE}")

subprocess.run(["systemctl", "restart", "home-assistant-flask.service"])
