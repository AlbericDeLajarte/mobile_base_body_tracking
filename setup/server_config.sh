#!/bin/bash

# This script sets up a Raspberry Pi as a Wi-Fi hotspot using NetworkManager

# Variables
SSID="TeloPi"
PASSWORD="teleop123" # Need to escape special characters
STATIC_IP="192.168.4.1"
NET_INTERFACE="wlan0"
CHANNEL="7"

# Update and install necessary packages
apt update
apt install -y hostapd iptables-persistent network-manager

# Stop and disable dnsmasq (since we will not be using it)
systemctl stop dnsmasq
systemctl disable dnsmasq
systemctl mask dnsmasq

# Stop services while configuring
systemctl stop hostapd

# Configure hostapd
cat > /etc/hostapd/hostapd.conf <<EOL
interface=$NET_INTERFACE
driver=nl80211
ssid=$SSID
hw_mode=g
channel=$CHANNEL
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=$PASSWORD
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOL

# Point hostapd to the configuration file
sed -i 's|#DAEMON_CONF="|DAEMON_CONF="/etc/hostapd/hostapd.conf|' /etc/default/hostapd

# Configure NetworkManager to manage the hotspot
nmcli connection add type wifi ifname $NET_INTERFACE con-name "Hotspot" autoconnect yes ssid $SSID
nmcli connection modify "Hotspot" 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared
nmcli connection modify "Hotspot" wifi-sec.key-mgmt wpa-psk wifi-sec.psk $PASSWORD
nmcli connection modify "Hotspot" ipv4.addresses $STATIC_IP/24

# Enable IP routing
sed -i 's|#net.ipv4.ip_forward=1|net.ipv4.ip_forward=1|' /etc/sysctl.conf
sysctl -p

# Set up NAT (Network Address Translation)
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sh -c "iptables-save > /etc/iptables.ipv4.nat"

# Ensure iptables rule is restored on boot
sed -i '$ i\iptables-restore < /etc/iptables.ipv4.nat' /etc/rc.local

## Configure script to start at power up

# Set the service name and script path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="trackerServer"
SCRIPT_PATH="$(realpath "$SCRIPT_DIR/../run_velocityTrackerServer.py")"
WORKING_DIR="$(realpath "$SCRIPT_DIR/../")"

# Create the systemd service file
CAN_SETUP="/sbin/ip link set can0 up type can bitrate 500000"
echo "$USER ALL=(ALL) NOPASSWD: $CAN_SETUP" | sudo EDITOR='tee -a' visudo

chmod +x $SCRIPT_DIR/setup_can.sh

echo "[Unit]
Description=Server for the velocity tracker
After=network.target hostapd.service

[Service]
ExecStartPre=/usr/bin/sudo $SCRIPT_DIR/setup_can.sh
ExecStart=$HOME/.pyenv/shims/python $SCRIPT_PATH
WorkingDirectory=$WORKING_DIR
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null

# Reload the systemd daemon to recognize the new service and enable it
systemctl daemon-reload

# Enable and start the services
systemctl unmask hostapd
systemctl enable hostapd
systemctl start hostapd
systemctl enable $SERVICE_NAME.service

# Start the NetworkManager connection
nmcli connection up "Hotspot"

# Make sure dnsmasq is stopped and disabled
systemctl stop dnsmasq
systemctl disable dnsmasq
systemctl mask dnsmasq

echo "Setup complete. The Raspberry Pi will now reboot."

sleep 2

# Restart the RPi
reboot
