#!/bin/bash

echo "Starting system load to test Netdata dashboard..."

echo "Running CPU stress test..."
stress --cpu 4 --timeout 60

echo "Running memory load test..."
stress --vm 2 --vm-bytes 512M --timeout 60