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
        """Sends a single metric payload to the server."""
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.full_url,
                    json=data,
                    timeout=self.timeout,
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code in [200, 201]:
                    return True
                else:
                    print(f"[Error] Server returned status {response.status_code}: {response.text}")

            except requests.exceptions.RequestException as e:
                print(f"[Error] Connection error on attempt {attempt + 1}/{self.max_retries}: {e}")

            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        print(f"[Error] Failed to send metric after {self.max_retries} attempts.")
        return False

    def send_batch(self, metrics: List[Dict[str, Any]]) -> bool:

        if not metrics:
            return True

        print(f"Transmitting a batch of {len(metrics)} metrics...")
        all_successful = True
        for i, metric in enumerate(metrics):
            print(f"Sending metric {i + 1}/{len(metrics)}...")
            if not self.send(metric):
                all_successful = False
                print(f"[Warning] Failed to send metric {i + 1} in the batch. Continuing with the rest.")

        if all_successful:
            print(f"Successfully sent all {len(metrics)} metrics in the batch.")
        else:
            print(f"Finished sending batch with one or more failures.")

        return all_successful