"""
GPU metrics collection.

Units:
- utilization_percent: percentage (%)
- memory_used_mb, memory_total_mb: MB
- temperature: Celsius (°C)
- power_watts: Watts (W)
"""

import subprocess
import platform
from typing import TypedDict, List
import time

OS_TYPE = platform.system()


class GPUInfo(TypedDict):
    index: int
    utilization_percent: float
    memory_used_mb: float
    memory_total_mb: float
    temperature: float
    power_watts: float


class GPUStatic(TypedDict):
    count: int
    names: List[str]


class GPUDynamic(TypedDict):
    gpus: List[GPUInfo]


def get_gpu_static_metadata() -> GPUStatic:
    count = 0
    names = []

    result = subprocess.run(
        ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
        capture_output=True, text=True, timeout=2
    )

    if result.returncode == 0:
        names = [name.strip() for name in result.stdout.strip().split('\n')]
        count = len(names)

    return {
        'count': count,
        'names': names
    }


def get_gpu_dynamic_metrics() -> GPUDynamic:
    gpus = []

    result = subprocess.run(
        ['nvidia-smi', '--query-gpu=index,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw', '--format=csv,noheader,nounits'],
        capture_output=True, text=True, timeout=2
    )

    if result.returncode == 0:
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 6:
                    gpus.append({
                        'index': int(parts[0]),
                        'utilization_percent': float(parts[1]) if parts[1] != '[N/A]' else -1,
                        'memory_used_mb': float(parts[2]) if parts[2] != '[N/A]' else -1,
                        'memory_total_mb': float(parts[3]) if parts[3] != '[N/A]' else -1,
                        'temperature': float(parts[4]) if parts[4] != '[N/A]' else -1,
                        'power_watts': float(parts[5]) if parts[5] != '[N/A]' else -1
                    })

    return {
        'gpus': gpus
    }


if __name__ == "__main__":
    start_time = time.perf_counter()

    print("=== GPU Static Metadata ===")
    static = get_gpu_static_metadata()
    for key, value in static.items():
        print(f"{key}: {value}")

    print("\n=== GPU Dynamic Metrics ===")
    dynamic = get_gpu_dynamic_metrics()
    for key, value in dynamic.items():
        print(f"{key}: {value}")

    elapsed = time.perf_counter() - start_time
    print(f"\nTime taken: {elapsed:.4f} seconds")
