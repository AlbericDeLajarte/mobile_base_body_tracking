#!/bin/bash

# This script sets up a Raspberry Pi as a Wi-Fi hotspot using NetworkManager

# Variables
SSID="TeloPi"
PASSWORD="Ada\$\$tra2029" # Need to escape special characters
STATIC_IP="192.168.4.1"
NET_INTERFACE="wlan0"
CHANNEL="7"

# Update and install necessary packages
apt update
apt install -y hostapd dnsmasq iptables-persistent network-manager

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

# Configure static IP for wlan0 using NetworkManager
nmcli connection add type wifi ifname $NET_INTERFACE con-name "Hotspot" autoconnect yes ssid $SSID
nmcli connection modify "Hotspot" 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared
nmcli connection modify "Hotspot" wifi-sec.key-mgmt wpa-psk wifi-sec.psk $PASSWORD
nmcli connection modify "Hotspot" ipv4.addresses $STATIC_IP/24
nmcli connection modify "Hotspot" ipv4.gateway $STATIC_IP

# Enable IP routing
sed -i 's|#net.ipv4.ip_forward=1|net.ipv4.ip_forward=1|' /etc/sysctl.conf
sysctl -p

# Set up NAT (Network Address Translation)
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sh -c "iptables-save > /etc/iptables.ipv4.nat"

# Ensure iptables rule is restored on boot
sed -i '$ i\iptables-restore < /etc/iptables.ipv4.nat' /etc/rc.local

# Enable and start the hostapd and dnsmasq services
systemctl unmask hostapd
systemctl enable hostapd
systemctl enable dnsmasq
systemctl start hostapd
systemctl start dnsmasq

# Start the NetworkManager connection
nmcli connection up "Hotspot"

echo "Setup complete. The Raspberry Pi will now reboot."

# Restart the RPi
reboot
