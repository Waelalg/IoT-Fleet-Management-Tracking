# devices/http_device.py
import requests
import time
import random
from datetime import datetime

class HTTPDevice:
    def __init__(self, device_id, device_type="http-device"):
        self.device_id = device_id
        self.device_type = device_type
        self.base_url = "http://backend:5002"
        self.lat = 34.89
        self.lon = -1.32
        self.battery = 85.0
        
    def generate_payload(self):
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "lat": self.lat + random.uniform(-0.001, 0.001),
            "lon": self.lon + random.uniform(-0.001, 0.001),
            "battery": max(0, self.battery - random.uniform(0.1, 0.5)),
            "temperature": random.uniform(20, 35),
            "status": "OK",
            "sensor_data": {
                "protocol": "http",
                "request_latency": random.uniform(10, 100),
                "signal_strength": random.randint(-120, -50)
            }
        }
        
    def send_telemetry(self):
        payload = self.generate_payload()
        try:
            response = requests.post(
                f"{self.base_url}/http/telemetry",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print(f"[HTTP {self.device_id}] ✓ Telemetry sent")
                return True
            else:
                print(f"[HTTP {self.device_id}] ✗ Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[HTTP {self.device_id}] ✗ Error: {e}")
            return False
            
    def run_continuous(self, interval=10):
        """Run device continuously"""
        print(f"[HTTP {self.device_id}] Starting HTTP device, interval: {interval}s")
        try:
            while True:
                self.send_telemetry()
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"[HTTP {self.device_id}] Stopping...")

if __name__ == "__main__":
    # Create and run an HTTP device
    device = HTTPDevice("http-continuous-01", "sensor")
    device.run_continuous(interval=15)