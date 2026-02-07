#!/bin/bash
set -e

# Must run as root
if [[ "$EUID" -ne 0 ]]; then
    echo "Please run this installer as root (sudo)."
    exit 1
fi

echo "Installing Dependencies..."
echo "Warning: This installs Python packages globally (no venv). Continue? (y/n)"

read -r response
if [[ "$response" != "y" && "$response" != "Y" ]]; then
    echo "Installation aborted."
    exit 1
fi

# Ensure HOME is correct (root => /root, user => /home/user)
HOME_DIR="$HOME"

echo "Updating system..."
apt update

echo "Installing packages..."
apt install -y \
    git \
    python3 \
    python3-pip \
    python3-flask \
    python3-flask-cors

echo "Cloning HASP repository..."
cd "$HOME_DIR"

if [[ ! -d HASP ]]; then
    git clone https://github.com/Jakobimatrix/HASP.git
else
    echo "HASP already exists, skipping clone."
fi

echo "Setting up configuration..."
cp -n "$HOME_DIR/HASP/config/template_config.py" "$HOME_DIR/HASP/config/config.py"
nano "$HOME_DIR/HASP/config/config.py"

echo "Do you want to install MQTT support? (y/n)"
read -r mqtt_response
if [[ "$mqtt_response" == "y" || "$mqtt_response" == "Y" ]]; then
    echo "Installing MQTT dependencies..."
    apt install mosquitto mosquitto-clients python3-paho-mqtt
    systemctl enable mosquitto
    systemctl start mosquitto
    

echo "Creating logs directory..."
mkdir -p "$HOME_DIR/HASP/logs"

echo "Setting up crontab for certificate renewal..."
CRON_LINE="0 2 1 1,4,7,10 * /usr/bin/python3 $HOME_DIR/HASP/scripts/renew_cert.py >> $HOME_DIR/HASP/logs/renew_cert.log 2>&1"
(crontab -l 2>/dev/null | grep -v renew_cert.py; echo "$CRON_LINE") | crontab -

echo "Installing certificates..."
python3 "$HOME_DIR/HASP/scripts/renew_cert.py"

echo "Installing systemd service..."

cat <<EOT > /etc/systemd/system/hasp.service
[Unit]
Description=HASP Flask Server
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$HOME_DIR/HASP
ExecStartPre=/bin/sleep 2
ExecStart=/usr/bin/python3 $HOME_DIR/HASP/server.py

Restart=always
RestartSec=5

StandardOutput=append:$HOME_DIR/HASP/logs/flask.out.log
StandardError=journal

[Install]
WantedBy=multi-user.target
EOT

echo "Reloading systemd..."
systemctl daemon-reexec
systemctl daemon-reload

echo "Enabling and starting service..."
systemctl enable hasp.service
systemctl restart hasp.service

echo "Creating admin user..."
cd "$HOME_DIR"
python3 -m scripts.newUser

echo "Installation complete."
echo "Access HASP at: https://<your-server-ip>:5000"
echo "Logs can be found in $HOME_DIR/HASP/logs/"