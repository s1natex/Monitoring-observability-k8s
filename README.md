# Simple-Monitoring
A basic monitoring dashboard using Netdata

## Project Page
```
https://roadmap.sh/projects/simple-monitoring-dashboard
```
# How to Use:
- Install git and clone repository
```
git clone https://github.com/s1natex/Simple-Monitoring
cd <to-repo-path>
```
- Grant permissions to setup.sh, test_dashboard.sh and cleanup.sh
```bash
sudo chmod +x setup.sh
sudo chmod +x test_dashboard.sh
sudo chmod +x cleanup.sh
```
- Run setup.sh and configure netdata.conf
```bash
./setup.sh

sudo vim /etc/netdata/netdata.conf
#Ensure the [plugins] section is correctly set to monitor the required metrics
#CPU, memory usage, and disk I/O
[plugins]
    cpu = yes
    mem = yes
    diskspace = yes
    diskio = yes

sudo systemctl restart netdata

#Find your ip address and access NetData dashboard
ip addr show
http://<your-server-ip>:19999
```

- Create a new chart configuration
```bash
sudo vim /etc/netdata/charts.d/custom_chart.conf
```
- Add a custom chart configuration
```
chart custom.system_usage '' "Custom System Usage" "Usage" "System" "line" 60000
options base 1024
dimension cpu_usage "CPU Usage" absolute 1 100
dimension memory_usage "Memory Usage" absolute 1 100
```
- Create a script to feed data to the chart
```
sudo vim /usr/lib/netdata/plugins.d/charts.d/custom_chart.sh
```
```
#!/bin/bash
while true; do
  cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
  mem=$(free | awk '/Mem/{printf("%.2f", $3/$2 * 100)}')
  echo "CHART custom.system_usage '' 'Custom System Usage' 'Usage' 'System' 'line' 60000"
  echo "DIMENSION cpu_usage $cpu"
  echo "DIMENSION memory_usage $mem"
  sleep 10
done
```
```
sudo chmod +x /usr/lib/netdata/plugins.d/charts.d/custom_chart.sh
```
```
sudo systemctl restart netdata
```
- Set Up an Alert for CPU Usage Above 80%
```
sudo vim /etc/netdata/health.d/cpu.conf
```
```
alarm: high_cpu_usage
  on: system.cpu
 lookup: average -1m
 units: %
 every: 10s
  warn: $this > 80
  info: CPU usage is above 80%.
  to: sysadmin
```
```
sudo systemctl restart netdata
```
- Run stress test
```
./test_dashboard.sh
```
- Access NetData dashboard and ensure data is shown and alert is active
```bash
#Find your ip address and access NetData dashboard
http://<your-server-ip>:19999
```
### Clean up Netdata from the system:
```bash
./cleanup.sh
```