# Simple System Monitor

Lightweight system monitoring tool with HTTP data transmission capabilities. **No ROS dependencies required.**

## 🚀 Features

- **Lightweight**: Pure Python implementation with minimal dependencies
- **Comprehensive Metrics**: CPU, Memory, Disk, Network monitoring
- **Batch Transmission**: Efficient bulk data transmission with retry logic
- **Configurable**: Easy configuration via YAML or command-line arguments
- **Robust**: Automatic retry mechanism with exponential backoff
- **Logging**: Detailed logging for debugging and monitoring

## 📋 Requirements

- Python 3.8+
- psutil
- requests
- pyyaml (optional, for config file support)

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/nevlife/simple-system-monitor.git
cd simple-system-monitor

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Quick Start

### Basic Usage

```bash
# Start monitoring with default settings (localhost:8000)
python monitor.py

# Specify custom server URL
python monitor.py --server-url http://your-server:8000

# Use configuration file
python monitor.py --config config.yaml
```

### Configuration Options

```bash
python monitor.py \
  --server-url http://localhost:8000 \
  --endpoint /api/system-metrics/ \
  --interval 1.0 \
  --batch-size 10 \
  --timeout 10 \
  --max-retries 3
```

## ⚙️ Configuration File

Create a `config.yaml` file:

```yaml
server:
  url: http://localhost:8000
  endpoint: /api/system-metrics/
  timeout: 10
  max_retries: 3

monitoring:
  interval: 1.0  # Collection interval in seconds
  batch_size: 10  # Number of metrics to batch before sending

logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR
  file: null  # Optional log file
```

## 📊 Collected Metrics

### CPU
- `cpu_percent`: Overall CPU usage percentage
- `cpu_cores`: Number of CPU cores
- `load_average`: System load average (1, 5, 15 minutes)

### Memory
- `memory_total`: Total memory in bytes
- `memory_used`: Used memory in bytes
- `memory_percent`: Memory usage percentage

### Disk
- `disk_total`: Total disk space in bytes
- `disk_used`: Used disk space in bytes
- `disk_percent`: Disk usage percentage

### Network
- `network_bytes_sent`: Total bytes sent
- `network_bytes_recv`: Total bytes received
- `network_packets_sent`: Total packets sent
- `network_packets_recv`: Total packets received

### System
- `hostname`: System hostname
- `timestamp`: Metric collection timestamp (ISO 8601)
- `uptime`: System uptime in seconds

## 📡 API Format

The monitor sends data to your server via HTTP POST in JSON format:

```json
{
  "metrics": [
    {
      "hostname": "myserver",
      "timestamp": "2025-10-01T12:00:00.000000",
      "cpu_percent": 25.5,
      "cpu_cores": 8,
      "load_average": [1.2, 1.5, 1.3],
      "memory_total": 17179869184,
      "memory_used": 8589934592,
      "memory_percent": 50.0,
      "disk_total": 500107862016,
      "disk_used": 250053931008,
      "disk_percent": 50.0,
      "network_bytes_sent": 1048576,
      "network_bytes_recv": 2097152,
      "network_packets_sent": 1000,
      "network_packets_recv": 2000,
      "uptime": 86400.0
    }
  ]
}
```

## 💡 Usage Examples

### Development Mode (High Frequency)

```bash
python monitor.py \
  --server-url http://localhost:8000 \
  --interval 0.1 \
  --batch-size 50
```

### Production Mode (Low Frequency)

```bash
python monitor.py \
  --server-url http://production-server:8000 \
  --interval 30 \
  --batch-size 1
```

### Debug Mode

```bash
python monitor.py --log-level DEBUG
```

## 🔧 Running as a Service

### systemd (Linux)

Create `/etc/systemd/system/system-monitor.service`:

```ini
[Unit]
Description=Simple System Monitor
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/simple-system-monitor
ExecStart=/usr/bin/python3 /path/to/simple-system-monitor/monitor.py --config /path/to/config.yaml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable system-monitor
sudo systemctl start system-monitor
sudo systemctl status system-monitor
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "monitor.py", "--config", "config.yaml"]
```

Build and run:

```bash
docker build -t system-monitor .
docker run -d --name monitor system-monitor
```

## 📈 Performance

- **CPU Impact**: ~0.1-0.5% at 1Hz collection rate
- **Memory Usage**: ~10-20MB
- **Network Bandwidth**: ~1-5KB per metric record

## 🐛 Troubleshooting

### Connection Errors

```bash
# Test server connectivity
curl -X POST http://your-server:8000/api/health/
```

### Permission Issues

Some metrics may require elevated privileges:

```bash
sudo python monitor.py
```

### Debug Logging

```bash
python monitor.py --log-level DEBUG
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License

## 🆚 Comparison with ROS2 Version

| Feature | simple-system-monitor | ros2_system_monitor |
|---------|----------------------|---------------------|
| Dependencies | Python + 2 packages | ROS2 + colcon + rclpy |
| Setup Complexity | Low | High |
| Memory Usage | ~10-20MB | ~30-50MB |
| Learning Curve | Easy | Steep |
| Use Case | General monitoring | ROS2 robot systems |

## 🔗 Related Projects

- [ros2_system_monitor](https://github.com/nevlife/ros2_system_monitor) - ROS2 version of this tool
