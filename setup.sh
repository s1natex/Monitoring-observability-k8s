echo "Updating system..."
sudo dnf update -y

echo "Installing Required Dependencies..."
sudo dnf install -y curl git zlib-devel gcc make automake autoconf pkgconfig \
python3 python3-pip python3-psutil \
nodejs npm \
perl

echo "Installing NetData..."
bash <(curl -Ss https://my-netdata.io/kickstart.sh)

echo "Starting and enabling Netdata service..."
sudo systemctl start netdata
sudo systemctl enable netdata

echo "Checking Netdata service status..."
sudo systemctl status netdata

echo
echo
echo
echo "NetData installation complete!"