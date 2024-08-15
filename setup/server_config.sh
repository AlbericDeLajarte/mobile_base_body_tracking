# Setup Rpi as Hotspot

sudo apt install hostapd dnsmasq -y
sudo systemctl stop hostapd

sudo echo "interface=wlan0 
driver=nl80211
ssid=TeleoPi
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=teleop123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP" > /etc/hostapd/hostapd.conf

# Point hostapd to this configuration file
sudo echo "DAEMON_CONF="/etc/hostapd/hostapd.conf"" >> /etc/default/hostapd

# DHCP server
sudo systemctl stop dnsmasq
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig && sudo nano /etc/dnsmasq.conf
sudo echo "interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h" > /etc/dnsmasq.conf

# Add static IP to wlan0
sudo echo "interface wlan0
static ip_address=192.168.4.1/24
nohook wpa_supplicant" >> /etc/dhcpcd.conf

# Enable IP Routing
sudo echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sudo sysctl -p

# Set Up NAT
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
sudo echo "iptables-restore < /etc/iptables.ipv4.nat" >> /etc/rc.local

# Restart services
sudo systemctl start hostapd
sudo systemctl start dnsmasq

sudo systemctl enable hostapd
sudo systemctl enable dnsmasq