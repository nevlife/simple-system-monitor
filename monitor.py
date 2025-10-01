#!/usr/bin/env python3
"""
Simple System Monitor

Lightweight system monitoring tool that collects system metrics
and transmits them to an HTTP server.
"""

import argparse
import json
import logging
import socket
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

import psutil
import requests

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class SystemMonitor:
    """Collects system metrics using psutil."""

    def __init__(self):
        self.hostname = socket.gethostname()
        self._last_net_io = psutil.net_io_counters()

    def collect_metrics(self) -> Dict:
        """Collect comprehensive system metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_cores = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]

            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net_io = psutil.net_io_counters()
            
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            timestamp = datetime.now().isoformat()

            return {
                'hostname': self.hostname,
                'timestamp': timestamp,
                'cpu_percent': cpu_percent,
                'cpu_cores': cpu_cores,
                'load_average': list(load_avg),
                'memory_total': memory.total,
                'memory_used': memory.used,
                'memory_percent': memory.percent,
                'disk_total': disk.total,
                'disk_used': disk.used,
                'disk_percent': disk.percent,
                'network_bytes_sent': net_io.bytes_sent,
                'network_bytes_recv': net_io.bytes_recv,
                'network_packets_sent': net_io.packets_sent,
                'network_packets_recv': net_io.packets_recv,
                'uptime': uptime
            }
        except Exception as e:
            logging.error(f"Error collecting metrics: {e}")
            return {}


class DataTransmitter:
    """Handles transmission of metrics to HTTP server."""

    def __init__(self, server_url: str, endpoint: str = '/api/system-metrics/',
                 timeout: int = 10, max_retries: int = 3):
        self.server_url = server_url.rstrip('/')
        self.endpoint = endpoint
        self.timeout = timeout
        self.max_retries = max_retries
        self.full_url = f"{self.server_url}{self.endpoint}"

    def send_metrics(self, metrics: List[Dict]) -> bool:
        """Send metrics to the server with retry logic."""
        if not metrics:
            return True

        payload = {'metrics': metrics}
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.full_url,
                    json=payload,
                    timeout=self.timeout,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code in [200, 201]:
                    logging.info(f"Successfully sent {len(metrics)} metrics to server")
                    return True
                else:
                    logging.warning(f"Server returned status {response.status_code}: {response.text}")
            except requests.exceptions.Timeout:
                logging.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries})")
            except requests.exceptions.ConnectionError:
                logging.warning(f"Connection error (attempt {attempt + 1}/{self.max_retries})")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
            
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                logging.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        
        logging.error(f"Failed to send metrics after {self.max_retries} attempts")
        return False


class MonitorService:
    """Main monitoring service."""

    def __init__(self, config: Dict):
        self.config = config
        self.monitor = SystemMonitor()
        self.transmitter = DataTransmitter(
            server_url=config['server']['url'],
            endpoint=config['server']['endpoint'],
            timeout=config['server']['timeout'],
            max_retries=config['server']['max_retries']
        )
        self.metrics_buffer: List[Dict] = []
        self.running = False

    def start(self):
        """Start the monitoring service."""
        self.running = True
        interval = self.config['monitoring']['interval']
        batch_size = self.config['monitoring']['batch_size']
        
        logging.info(f"Starting system monitor...")
        logging.info(f"Server: {self.config['server']['url']}")
        logging.info(f"Interval: {interval}s, Batch size: {batch_size}")
        
        try:
            while self.running:
                metrics = self.monitor.collect_metrics()
                if metrics:
                    self.metrics_buffer.append(metrics)
                    logging.debug(f"Collected metrics: CPU={metrics['cpu_percent']}%, "
                                f"MEM={metrics['memory_percent']}%")
                
                if len(self.metrics_buffer) >= batch_size:
                    self._flush_buffer()
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logging.info("Received shutdown signal")
        finally:
            self.stop()

    def stop(self):
        """Stop the monitoring service."""
        self.running = False
        if self.metrics_buffer:
            logging.info("Flushing remaining metrics...")
            self._flush_buffer()
        logging.info("Monitor stopped")

    def _flush_buffer(self):
        """Send buffered metrics to server."""
        if not self.metrics_buffer:
            return
        
        success = self.transmitter.send_metrics(self.metrics_buffer)
        if success:
            self.metrics_buffer.clear()
        else:
            logging.warning(f"Failed to send {len(self.metrics_buffer)} metrics. Keeping in buffer.")


def load_config(config_file: Optional[str] = None, args=None) -> Dict:
    """Load configuration from file or command-line arguments."""
    config = {
        'server': {
            'url': 'http://localhost:8000',
            'endpoint': '/api/system-metrics/',
            'timeout': 10,
            'max_retries': 3
        },
        'monitoring': {
            'interval': 1.0,
            'batch_size': 10
        },
        'logging': {
            'level': 'INFO',
            'file': None
        }
    }
    
    if config_file and YAML_AVAILABLE:
        try:
            with open(config_file, 'r') as f:
                file_config = yaml.safe_load(f)
                for section in file_config:
                    if section in config:
                        config[section].update(file_config[section])
            logging.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            logging.warning(f"Could not load config file: {e}")
    
    if args:
        if args.server_url:
            config['server']['url'] = args.server_url
        if args.endpoint:
            config['server']['endpoint'] = args.endpoint
        if args.interval:
            config['monitoring']['interval'] = args.interval
        if args.batch_size:
            config['monitoring']['batch_size'] = args.batch_size
        if args.timeout:
            config['server']['timeout'] = args.timeout
        if args.max_retries:
            config['server']['max_retries'] = args.max_retries
        if args.log_level:
            config['logging']['level'] = args.log_level
        if args.log_file:
            config['logging']['file'] = args.log_file
    
    return config


def setup_logging(level: str = 'INFO', log_file: Optional[str] = None):
    """Configure logging."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Simple System Monitor - Collect and transmit system metrics'
    )
    
    parser.add_argument('--config', type=str, help='Path to YAML configuration file')
    parser.add_argument('--server-url', type=str, help='Server URL')
    parser.add_argument('--endpoint', type=str, help='API endpoint path')
    parser.add_argument('--timeout', type=int, help='HTTP timeout in seconds')
    parser.add_argument('--max-retries', type=int, help='Maximum retry attempts')
    parser.add_argument('--interval', type=float, help='Collection interval in seconds')
    parser.add_argument('--batch-size', type=int, help='Number of metrics per batch')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    parser.add_argument('--log-file', type=str, help='Log file path')
    
    args = parser.parse_args()
    
    config = load_config(args.config, args)
    setup_logging(config['logging']['level'], config['logging']['file'])
    
    service = MonitorService(config)
    service.start()


if __name__ == '__main__':
    main()
