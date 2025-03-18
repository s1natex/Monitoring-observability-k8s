#!/bin/bash

# Stop Netdata service
echo "Stopping Netdata service..."
sudo systemctl stop netdata

# Remove Netdata
echo "Removing Netdata..."
sudo apt remove --purge -y netdata

# Clean up configuration files
echo "Cleaning up configuration files..."
sudo rm -rf /etc/netdata

# Check if Netdata is still installed
echo "Checking if Netdata is still installed..."
dpkg -l | grep netdata

sudo systemctl disable firewalld
sudo systemctl stop firewalld

echo "Cleanup complete!"