#!/bin/bash

echo "Starting system stress test to monitor Netdata dashboard..."
sudo dnf install -y stress
# CPU Stress Test
echo "Running CPU stress test: 4 CPU workers for 60 seconds..."
stress --cpu 4 --timeout 60
echo "CPU stress test completed."

# Memory Stress Test
echo "Running memory stress test: 2 workers with 512MB each for 60 seconds..."
stress --vm 2 --vm-bytes 512M --timeout 60
echo "Memory stress test completed."

echo "System stress test finished. Check Netdata dashboard for metrics."
