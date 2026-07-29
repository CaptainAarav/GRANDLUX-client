import requests
import threading
import time

class DataSender:
    def __init__(self, listener, api_url, token, interval=10):
        self.listener = listener
        self.api_url = api_url
        self.token = token
        self.interval = interval
        self._running = False
        
    def start(self) -> None:
        self._running = True
        thread = threading.Thread(target=self._send_loop, daemon=True)
        thread.start()
        
    def stop(self) -> None:
        self._running = False
    
    def _send_loop(self) -> None:
        while self._running:
            data = self.listener.get_latest()
            if not data:
                time.sleep(self.interval)
                continue 
            
            self._send(data)
            time.sleep(self.interval)
            
    def _send(self, data: dict) -> None:
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.post(self.api_url, json=data, headers=headers, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Send failed: {e}")