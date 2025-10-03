"""
Network metrics collection.

Units:
- bytes_sent, bytes_recv: bytes (cumulative)
- packets_sent, packets_recv: count (cumulative)
- errin, errout, dropin, dropout: count (cumulative)
- speed: Mbps
- mtu: bytes
"""

import psutil
import platform
from typing import TypedDict, List, Dict, Any
import time

OS_TYPE = platform.system()


class NetworkStatic(TypedDict):
    interfaces: List[str]
    mtu: Dict[str, int]
    speed: Dict[str, int]


class NetworkDynamic(TypedDict):
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int
    connection_count: int


def get_network_static_metadata() -> NetworkStatic:
    interfaces = list(psutil.net_if_addrs().keys())
    stats = psutil.net_if_stats()

    mtu = {name: stat.mtu for name, stat in stats.items()}
    speed = {name: stat.speed for name, stat in stats.items()}

    return {
        'interfaces': interfaces,
        'mtu': mtu,
        'speed': speed
    }


def get_network_dynamic_metrics() -> NetworkDynamic:
    io = psutil.net_io_counters(pernic=False)
    conns = psutil.net_connections(kind='inet')

    return {
        'bytes_sent': io.bytes_sent,
        'bytes_recv': io.bytes_recv,
        'packets_sent': io.packets_sent,
        'packets_recv': io.packets_recv,
        'errin': io.errin,
        'errout': io.errout,
        'dropin': io.dropin,
        'dropout': io.dropout,
        'connection_count': len(conns)
    }


if __name__ == "__main__":
    start_time = time.perf_counter()

    print("=== Network Static Metadata ===")
    static = get_network_static_metadata()
    for key, value in static.items():
        print(f"{key}: {value}")

    print("\n=== Network Dynamic Metrics ===")
    dynamic = get_network_dynamic_metrics()
    for key, value in dynamic.items():
        print(f"{key}: {value}")

    elapsed = time.perf_counter() - start_time
    print(f"\nTime taken: {elapsed:.4f} seconds")
