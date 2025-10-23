# devices/coap_device.py
import requests
import time
import random
from datetime import datetime

class CoAPDevice:
    def __init__(self, device_id, device_type="coap-device"):
        self.device_id = device_id
        self.device_type = device_type
        self.base_url = "http://backend:5002"  # Using HTTP bridge for CoAP
        self.lat = 34.89
        self.lon = -1.32
        self.battery = 90.0  # CoAP devices often have better battery
        
    def generate_payload(self):
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "lat": self.lat + random.uniform(-0.0005, 0.0005),  # Less movement
            "lon": self.lon + random.uniform(-0.0005, 0.0005),
            "battery": max(0, self.battery - random.uniform(0.05, 0.2)),  # Slower drain
            "temperature": random.uniform(15, 30),
            "status": "OK",
            "sensor_data": {
                "protocol": "coap",
                "battery_voltage": random.uniform(3.0, 4.2),
                "packet_loss": random.uniform(0, 2),  # Low packet loss
                "message_size": random.randint(50, 200)  # Small messages
            }
        }
        
    def send_telemetry(self):
        payload = self.generate_payload()
        try:
            response = requests.post(
                f"{self.base_url}/coap/telemetry",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print(f"[CoAP {self.device_id}] ✓ Telemetry sent")
                return True
            else:
                print(f"[CoAP {self.device_id}] ✗ Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[CoAP {self.device_id}] ✗ Error: {e}")
            return False
            
    def run_continuous(self, interval=30):
        """Run device continuously (CoAP devices send less frequently)"""
        print(f"[CoAP {self.device_id}] Starting CoAP device, interval: {interval}s")
        try:
            while True:
                self.send_telemetry()
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"[CoAP {self.device_id}] Stopping...")

if __name__ == "__main__":
    # Create and run a CoAP device
    device = CoAPDevice("coap-continuous-01", "sensor")
    device.run_continuous(interval=30)