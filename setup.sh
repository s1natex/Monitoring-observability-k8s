echo "Updating system..."
sudo dnf update -y

echo "Installing Required Dependencies..."
sudo dnf install -y curl git zlib-devel gcc make automake autoconf pkgconfig \
python3 python3-pip python3-psutil \
nodejs npm \
perl

echo "Installing NetData..."
bash <(curl -L -Ss https://my-netdata.io/kickstart.sh) --yes

echo "Starting and enabling Netdata service..."
sudo systemctl start netdata
sudo systemctl enable netdata

echo "Checking Netdata service status..."
sudo systemctl status netdata
sudo netdatacli dumpconfig > /etc/netdata/netdata.conf

sudo systemctl start firewalld
sudo systemctl enable firewalld
sudo firewall-cmd --add-port=19999/tcp --permanent
sudo firewall-cmd --reload
sudo mkdir -p /etc/netdata/charts.d
sudo touch /etc/netdata/charts.d/custom_chart.conf

sudo mkdir -p /usr/lib/netdata/plugins.d/charts.d
sudo touch /usr/lib/netdata/plugins.d/charts.d/custom_chart.sh


echo
echo
echo
echo "NetData installation complete!"