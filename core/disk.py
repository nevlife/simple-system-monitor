"""
Disk metrics collection.

Units:
- total, used, free: bytes
- percent: percentage (%)
- read_count, write_count: count (cumulative)
- read_bytes, write_bytes: bytes (cumulative)
- read_time, write_time: milliseconds (cumulative)
- read_merged_count, write_merged_count: count (cumulative, Linux only)
- busy_time: milliseconds (cumulative, Linux only)
"""

import psutil
import platform
from typing import TypedDict, List
import time

OS_TYPE = platform.system()


class DiskPartition(TypedDict):
    device: str
    mountpoint: str
    fstype: str
    opts: str


class DiskStatic(TypedDict):
    partitions: List[DiskPartition]
    devices: List[str]


class DiskIOCounters(TypedDict):
    read_count: int
    write_count: int
    read_bytes: int
    write_bytes: int
    read_time: int
    write_time: int
    read_merged_count: int
    write_merged_count: int
    busy_time: int


class DiskUsage(TypedDict):
    total: int
    used: int
    free: int
    percent: float


def get_disk_static_metadata() -> DiskStatic:
    partitions = []
    for part in psutil.disk_partitions(all=True):
        partitions.append({
            'device': part.device,
            'mountpoint': part.mountpoint,
            'fstype': part.fstype,
            'opts': part.opts
        })

    io = psutil.disk_io_counters(perdisk=True)
    devices = list(io.keys()) if io else []

    return {
        'partitions': partitions,
        'devices': devices
    }


def get_disk_usage_per_partition() -> dict[str, DiskUsage | None]:
    usage_per_partition = {}
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            usage_per_partition[part.mountpoint] = {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            }
        except (PermissionError, FileNotFoundError, SystemError):
            # Assign None if the drive is not accessible (e.g., encrypted and locked)
            usage_per_partition[part.mountpoint] = None
    return usage_per_partition


def get_disk_io_total() -> DiskIOCounters:
    io = psutil.disk_io_counters(perdisk=False)

    read_merged_count = -1
    write_merged_count = -1
    busy_time = -1

    match OS_TYPE:
        case 'Linux':
            read_merged_count = io.read_merged_count
            write_merged_count = io.write_merged_count
            busy_time = io.busy_time
        case 'Darwin' | 'Windows':
            pass

    return {
        'read_count': io.read_count,
        'write_count': io.write_count,
        'read_bytes': io.read_bytes,
        'write_bytes': io.write_bytes,
        'read_time': io.read_time,
        'write_time': io.write_time,
        'read_merged_count': read_merged_count,
        'write_merged_count': write_merged_count,
        'busy_time': busy_time
    }


if __name__ == "__main__":
    start_time = time.perf_counter()

    print("=== Disk Static Metadata ===")
    static = get_disk_static_metadata()
    for key, value in static.items():
        print(f"{key}: {value}")

    print("\n=== Disk Usage per Partition ===")
    usage = get_disk_usage_per_partition()
    for partition, values in usage.items():
        print(f"{partition}: {values}")

    print("\n=== Total Disk IO Counters ===")
    io_total = get_disk_io_total()
    print(io_total)

    elapsed = time.perf_counter() - start_time
    print(f"\nTime taken: {elapsed:.4f} seconds")
