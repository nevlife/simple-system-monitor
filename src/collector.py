from typing import Dict, Any
from core import cpu, memory, disk, network, gpu, system


class MetricsCollector:

    def __init__(self, enabled_modules: Dict[str, bool], client_id: str):
        self.enabled_modules = enabled_modules
        self.client_id = client_id

        network.get_network_info()

    def get_full_metrics(self) -> Dict[str, Any]:
        """
        Collects all enabled dynamic metrics from the core modules and returns
        them as a single dictionary, sending the raw data as requested.
        """
        payload: Dict[str, Any] = {
            'client_id': self.client_id
        }

        if self.enabled_modules.get('cpu', True):
            payload['cpu'] = cpu.get_cpu_dynamic_metrics()

        if self.enabled_modules.get('memory', True):
            payload['memory'] = memory.get_memory_dynamic_metrics()

        if self.enabled_modules.get('disk', True):
            payload['disk'] = {
                'usage_per_partition': disk.get_disk_usage_per_partition(),
                'io_total': disk.get_disk_io_total()
            }

        if self.enabled_modules.get('network', True):
            payload['network'] = network.get_network_info()
        
        if self.enabled_modules.get('system', True):
            payload['system'] = system.get_system_dynamic_metrics()
        
        if self.enabled_modules.get('gpu', True):
            try:
                payload['gpu'] = gpu.get_gpu_dynamic_metrics()
            except AttributeError:
                payload['gpu'] = None

        return payload
