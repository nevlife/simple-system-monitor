"""
CPU metrics collection.

Units:
- freq_min, freq_max, freq_current: MHz
- temperature: Celsius (°C)
- load_average: 1/5/15 minute averages
- user, system, idle, iowait: seconds
- ctx_switches, interrupts, soft_interrupts: count
- usage_percent: percentage (%)
"""

import psutil
import platform
from typing import TypedDict
import time

OS_TYPE = platform.system()

class CPUStatic(TypedDict):
    logical_cores: int
    physical_cores: int
    freq_min: float
    freq_max: float


class CPUDynamic(TypedDict):
    usage_percent: float
    freq_current: float
    temperature: float | int
    load_average: tuple | int
    iowait: float | int
    user: float
    system: float
    idle: float
    ctx_switches: int
    interrupts: int
    soft_interrupts: int


def get_cpu_static_metadata() -> CPUStatic:
    freq = psutil.cpu_freq()
    return {
        'logical_cores': psutil.cpu_count(logical=True),
        'physical_cores': psutil.cpu_count(logical=False),
        'freq_min': freq.min,
        'freq_max': freq.max
    }


def get_cpu_dynamic_metrics() -> CPUDynamic:
    times = psutil.cpu_times()
    stats = psutil.cpu_stats()
    freq = psutil.cpu_freq()

    temperature = -1
    load_average = -1
    iowait = -1

    match OS_TYPE:
        case 'Linux':
            temps = psutil.sensors_temperatures()
            sensor_list = temps.get('coretemp', temps.get('cpu_thermal', temps.get('k10temp', temps.get('zenpower', []))))
            temperature = sensor_list[0].current if sensor_list else -1
            load_average = psutil.getloadavg()
            iowait = times.iowait
        case 'Darwin':
            load_average = psutil.getloadavg()
            iowait = times.iowait
        case 'Windows':
            pass

    return {
        'usage_percent': psutil.cpu_percent(interval=0.1),
        'freq_current': freq.current,
        'temperature': temperature,
        'load_average': load_average,
        'iowait': iowait,
        'user': times.user,
        'system': times.system,
        'idle': times.idle,
        'ctx_switches': stats.ctx_switches,
        'interrupts': stats.interrupts,
        'soft_interrupts': stats.soft_interrupts
    }


if __name__ == "__main__":
    start_time = time.perf_counter()

    print("=== CPU Static Metadata ===")
    static = get_cpu_static_metadata()
    for key, value in static.items():
        print(f"{key}: {value}")

    print("\n=== CPU Dynamic Metrics ===")
    dynamic = get_cpu_dynamic_metrics()
    for key, value in dynamic.items():
        print(f"{key}: {value}")

    elapsed = time.perf_counter() - start_time
    print(f"\nTime taken: {elapsed:.4f} seconds")
