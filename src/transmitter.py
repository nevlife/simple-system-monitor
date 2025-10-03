import requests
from typing import Dict, Any, List
import time

class HTTPTransmitter:

    def __init__(self, server_url: str, endpoint: str, timeout: int, max_retries: int):
        self.server_url = server_url.rstrip('/')
        self.endpoint = endpoint
        self.timeout = timeout
        self.max_retries = max_retries
        self.full_url = f"{self.server_url}{self.endpoint}"

    def send(self, data: Dict[str, Any]) -> bool:
        return self.send_batch([data])

    def send_batch(self, metrics: List[Dict[str, Any]]) -> bool:
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
                    print(f"Successfully sent {len(metrics)} metrics to server")
                    return True
                else:
                    print(f"Server returned status {response.status_code}: {response.text}")

            except requests.exceptions.RequestException as e:
                print(f"Connection error on attempt {attempt + 1}/{self.max_retries}: {e}")

            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        print(f"Failed to send metrics after {self.max_retries} attempts")
        return False
