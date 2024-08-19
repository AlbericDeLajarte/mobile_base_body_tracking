#!/bin/bash

# Set the service name and script path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="trackerClient"
SCRIPT_PATH="$(realpath "$SCRIPT_DIR/../run_velocityTrackerClient.py")"
WORKING_DIR="$(realpath "$SCRIPT_DIR/../")"

# Create the systemd service file
echo "[Unit]
Description=Client for the velocity tracker
After=network.target

[Service]
ExecStart=/home/pi/.pyenv/shims/python $SCRIPT_PATH
WorkingDirectory=$WORKING_DIR
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null

# Reload the systemd daemon to recognize the new service and enable it
systemctl daemon-reload
systemctl enable $SERVICE_NAME.service

# Restart the RPi
echo "Setup complete. The Raspberry Pi will now reboot."
sleep 2
reboot