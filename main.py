from src.config_loader import load_config, get_server_config, get_collector_config, get_client_config
from src.collector import MetricsCollector
from src.transmitter import HTTPTransmitter
from src.monitor_service import MonitorService


def main():
    config = load_config('config.yaml')

    server_cfg = get_server_config(config)
    collector_cfg = get_collector_config(config)
    client_cfg = get_client_config(config)

    client_id = client_cfg.get('id')
    if not client_id:
        raise ValueError("client id not found in config.yaml under client section")

    collector = MetricsCollector(
        enabled_modules=collector_cfg.get('modules'),
        client_id=client_id
    )

    transmitter = HTTPTransmitter(
        server_url=server_cfg.get('url'),
        endpoint=server_cfg.get('endpoint'),
        timeout=server_cfg.get('timeout'),
        max_retries=server_cfg.get('max_retries')
    )

    service = MonitorService(
        collector=collector,
        transmitter=transmitter,
        interval=collector_cfg.get('interval'),
        batch_size=collector_cfg.get('batch_size')
    )

    service.start()

if __name__ == "__main__":
    main()
