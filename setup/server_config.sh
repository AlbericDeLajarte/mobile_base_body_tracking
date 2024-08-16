#!/bin/bash

# This script sets up a Raspberry Pi as a Wi-Fi hotspot

# Variables
SSID="TeloPi"
PASSWORD="Ada\$\$tra2029" # Need to escape special characters
STATIC_IP="192.168.4.1"
NET_INTERFACE="wlan0"
CHANNEL="7"

# Update and install necessary packages
apt update
apt install -y hostapd dnsmasq iptables-persistent

# Stop services while configuring
systemctl stop hostapd
systemctl stop dnsmasq

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

# Configure dnsmasq
mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
cat > /etc/dnsmasq.conf <<EOL
interface=$NET_INTERFACE
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
EOL

# Configure static IP for wlan0
cat >> /etc/dhcpcd.conf <<EOL
interface $NET_INTERFACE
static ip_address=$STATIC_IP/24
nohook wpa_supplicant
EOL

# Restart dhcpcd to apply IP configuration
systemctl restart dhcpcd

# Enable IP routing
sed -i 's|#net.ipv4.ip_forward=1|net.ipv4.ip_forward=1|' /etc/sysctl.conf
sysctl -p

# Set up NAT (Network Address Translation)
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sh -c "iptables-save > /etc/iptables.ipv4.nat"

# Ensure iptables rule is restored on boot
sed -i '$ i\iptables-restore < /etc/iptables.ipv4.nat' /etc/rc.local

# Uncomment if you want to ensure wlan0 is disconnected before setting up hotspot
# nmcli device disconnect $NET_INTERFACE

# Enable and start the hostapd and dnsmasq services
systemctl unmask hostapd
systemctl enable hostapd
systemctl enable dnsmasq
systemctl start hostapd
systemctl start dnsmasq

echo "Setup complete. The Raspberry Pi will now reboot."

# Restart the RPi
reboot
