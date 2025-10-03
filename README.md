# System Monitor

Modern Python system monitoring tool with HTTP transmission capabilities.

## Requirements

- Python 3.10+
- psutil
- requests
- pyyaml

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/system-monitor.git
cd system-monitor

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

1.  **Create Configuration File**: Create a file named `config.yaml` in the project root with the following content. Adjust the values as needed.

    ```yaml
    server:
      url: http://localhost:8000
      endpoint: /api/metrics
      timeout: 10
      max_retries: 3

    collector:
      interval: 1.0
      batch_size: 10
      modules:
        cpu: true
        memory: true
        disk: true
        network: true
        gpu: true
        system: true

    logging:
      level: INFO
      file: null
    ```

2.  **Run Monitor**:
    ```bash
    python main.py
    ```

## Configuration

## Collected Metrics

### Static Metadata (Collected Once)

**CPU:**
- logical_cores, physical_cores: count
- freq_min, freq_max: MHz

**Memory:**
- total, swap_total: bytes

**Disk:**
- partitions: [{device, mountpoint, fstype, opts}]
- devices: [device names]

**Network:**
- interfaces: [interface names]
- mtu: {interface: bytes}
- speed: {interface: Mbps}

**GPU (NVIDIA):**
- count: int
- names: [GPU names]

**System:**
- hostname, os info, python_version
- boot_time: Unix timestamp

### Dynamic Metrics (Collected Periodically)

**CPU:**
- usage_percent: %
- freq_current: MHz
- temperature: °C (Linux only)
- load_average: [1min, 5min, 15min] (Linux/macOS)
- user, system, idle, iowait: seconds
- ctx_switches, interrupts: count

**Memory:**
- total, available, used, free: bytes
- percent: %
- active, inactive, buffers, cached, shared, slab: bytes (Linux only)
- swap_used, swap_free, swap_percent
- swap_sin, swap_sout: bytes (Linux only)

**Disk:**
- **usage_per_partition**: A dictionary mapping each partition's mountpoint to its usage stats (`total`, `used`, `free`, `percent`) or `null` if inaccessible.
- **io_total**: Global disk IO counters (`read_count`, `write_count`, `read_bytes`, `write_bytes`, etc.).

**Network:**
- bytes_sent, bytes_recv: bytes
- packets_sent, packets_recv: count
- errin, errout, dropin, dropout: count
- connection_count: int

**GPU (NVIDIA):**
- gpus: [{index, utilization_percent, memory_used_mb, memory_total_mb, temperature, power_watts}]

**System:**
- timestamp: ISO 8601
- uptime: seconds
- users: [{name, terminal, host, started}]

## Architecture

### Platform-Specific Behavior

**Linux:**
- Full metrics support
- CPU temperature sensors
- Memory: active/inactive/buffers/cached/shared/slab
- Disk: merged I/O counts, busy time
- Network: all metrics

**macOS:**
- CPU: load_average, iowait
- Memory: active/inactive
- Disk/Network: basic metrics

**Windows:**
- Basic CPU/Memory/Disk/Network metrics
- No temperature, load_average, iowait

## API Format

**Payload Structure:**

```json
{
  "metrics": [
    {
      "static": {
        "cpu": {"logical_cores": 16, "physical_cores": 8, "..."},
        "memory": {"total": 17179869184, "..."},
        "disk": {"..."),
        "network": {"..."),
        "gpu": {"..."),
        "system": {"..."}
      },
      "dynamic": {
        "cpu": {"usage_percent": 25.5, "temperature": 45.2, "..."},
        "memory": {"used": 8589934592, "percent": 50.0, "..."},
        "disk": {
          "usage_per_partition": {
            "C:\\": {
              "total": 999219523584,
              "used": 184818352128,
              "free": 814401171456,
              "percent": 18.5
            },
            "D:\\": null
          },
          "io_total": {
            "read_count": 7573416,
            "write_count": 18291522,
            "read_bytes": 448069577728,
            "write_bytes": 554389483520,
            "..."
          }
        },
        "network": {"..."),
        "gpu": {"..."),
        "system": {"..."}
      }
    }
  ]
}
```

## Advanced Usage

### Custom Collector

```python
from src.collector import MetricsCollector

collector = MetricsCollector(enabled_modules={
    'cpu': True,
    'memory': True,
    'disk': False,
    'network': False,
    'gpu': False,
    'system': True
})

metrics = collector.get_full_metrics()
print(metrics)
```

### Custom Transmitter

```python
from src.transmitter import HTTPTransmitter

transmitter = HTTPTransmitter(
    server_url='https://api.example.com',
    endpoint='/v1/telemetry',
    timeout=30,
    max_retries=5
)

transmitter.send_batch([metrics])
```

## License

MIT License
