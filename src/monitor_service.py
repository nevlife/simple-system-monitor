"""Main monitoring service."""

import time
import json
from typing import Dict, Any, List

from src.collector import MetricsCollector
from src.transmitter import HTTPTransmitter


class MonitorService:
    
    def __init__(self, collector: MetricsCollector, transmitter: HTTPTransmitter, interval: float, batch_size: int):
        self.collector = collector
        self.transmitter = transmitter
        self.interval = interval
        self.batch_size = batch_size
        self.buffer: List[Dict[str, Any]] = []
        self.running = False

    def start(self):
        self.running = True

        print(f"Starting system monitor...")
        print(f"Interval: {self.interval}s, Batch size: {self.batch_size}")

        # printed_once = False
        try:
            while self.running:
                metrics = self.collector.get_full_metrics()

                # if not printed_once:
                #     print(json.dumps(metrics, indent=2, ensure_ascii=False))
                #     printed_once = True

                self.buffer.append(metrics)

                if len(self.buffer) >= self.batch_size:
                    self._flush_buffer()

                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\nReceived shutdown signal")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        if self.buffer:
            print("Flushing remaining metrics...")
            self._flush_buffer()
        print("Monitor stopped")

    def _flush_buffer(self):
        if not self.buffer:
            return

        success = self.transmitter.send_batch(self.buffer)
        if success:
            print(f"Sent {len(self.buffer)} metrics")
            self.buffer.clear()
        else:
            print(f"Failed to send {len(self.buffer)} metrics")
