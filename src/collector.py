from typing import Dict, Any
from core import cpu, memory, disk, network, gpu, system


class MetricsCollector:

    def __init__(self, enabled_modules: Dict[str, bool]):
        self.enabled_modules = enabled_modules
        self.static_metadata = self._collect_static_once()

    def _collect_static_once(self) -> Dict[str, Any]:
        static = {}

        if self.enabled_modules.get('cpu', True):
            static['cpu'] = cpu.get_cpu_static_metadata()

        if self.enabled_modules.get('memory', True):
            static['memory'] = memory.get_memory_static_metadata()

        if self.enabled_modules.get('disk', True):
            static['disk'] = disk.get_disk_static_metadata()

        if self.enabled_modules.get('network', True):
            static['network'] = network.get_network_static_metadata()

        if self.enabled_modules.get('gpu', True):
            static['gpu'] = gpu.get_gpu_static_metadata()

        if self.enabled_modules.get('system', True):
            static['system'] = system.get_system_static_metadata()

        return static

    def collect_dynamic(self) -> Dict[str, Any]:
        dynamic = {}

        if self.enabled_modules.get('cpu', True):
            dynamic['cpu'] = cpu.get_cpu_dynamic_metrics()

        if self.enabled_modules.get('memory', True):
            dynamic['memory'] = memory.get_memory_dynamic_metrics()

        if self.enabled_modules.get('disk', True):
            dynamic['disk'] = {
                'usage_per_partition': disk.get_disk_usage_per_partition(),
                'io_total': disk.get_disk_io_total()
            }

        if self.enabled_modules.get('network', True):
            dynamic['network'] = network.get_network_dynamic_metrics()

        if self.enabled_modules.get('gpu', True):
            dynamic['gpu'] = gpu.get_gpu_dynamic_metrics()

        if self.enabled_modules.get('system', True):
            dynamic['system'] = system.get_system_dynamic_metrics()

        return dynamic

    def get_full_metrics(self) -> Dict[str, Any]:
        return {
            'static': self.static_metadata,
            'dynamic': self.collect_dynamic()
        }
