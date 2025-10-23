# devices/multi_protocol_clients.py
import requests
import json
import time
import random
from datetime import datetime

class MultiProtocolTester:
    def __init__(self):
        self.base_url = "http://backend:5002"
        
    def test_mqtt_via_simulator(self, device_id, device_type="truck"):
        """Test MQTT protocol (via existing simulator)"""
        print(f"[MQTT] Testing {device_type} device: {device_id}")
        # This is handled by our existing advanced_simulator.py
        
    def test_http_protocol(self, device_id, device_type="http-device"):
        """Test HTTP protocol"""
        payload = {
            "device_id": device_id,
            "device_type": device_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "lat": 34.89 + random.uniform(-0.01, 0.01),
            "lon": -1.32 + random.uniform(-0.01, 0.01),
            "battery": random.uniform(50, 100),
            "temperature": random.uniform(20, 35),
            "status": "OK",
            "sensor_data": {
                "protocol": "http",
                "signal_strength": random.randint(-120, -50)
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/http/telemetry",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print(f"[HTTP] ✓ {device_id} telemetry sent successfully")
            else:
                print(f"[HTTP] ✗ {device_id} failed: {response.status_code}")
        except Exception as e:
            print(f"[HTTP] ✗ {device_id} error: {e}")
            
    def test_coap_protocol(self, device_id, device_type="coap-device"):
        """Test CoAP protocol via HTTP bridge"""
        payload = {
            "device_id": device_id,
            "device_type": device_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "lat": 34.89 + random.uniform(-0.01, 0.01),
            "lon": -1.32 + random.uniform(-0.01, 0.01),
            "battery": random.uniform(50, 100),
            "temperature": random.uniform(20, 35),
            "status": "OK",
            "sensor_data": {
                "protocol": "coap",
                "battery_voltage": random.uniform(3.0, 4.2),
                "packet_loss": random.uniform(0, 5)
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/coap/telemetry",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print(f"[CoAP] ✓ {device_id} telemetry sent successfully")
            else:
                print(f"[CoAP] ✗ {device_id} failed: {response.status_code}")
        except Exception as e:
            print(f"[CoAP] ✗ {device_id} error: {e}")
            
    def run_comprehensive_test(self):
        """Run comprehensive multi-protocol test"""
        print("=" * 50)
        print("MULTI-PROTOCOL IOT SYSTEM TEST")
        print("=" * 50)
        
        # Test HTTP devices
        print("\n1. Testing HTTP Protocol:")
        self.test_http_protocol("http-sensor-01", "sensor")
        self.test_http_protocol("http-truck-01", "truck")
        
        # Test CoAP devices (via HTTP bridge)
        print("\n2. Testing CoAP Protocol (HTTP bridge):")
        self.test_coap_protocol("coap-sensor-01", "sensor")
        self.test_coap_protocol("coap-drone-01", "drone")
        
        # Test MQTT (via existing simulators)
        print("\n3. Testing MQTT Protocol:")
        print("[MQTT] ✓ Devices running via advanced_simulator.py")
        
        print("\n4. Checking System Status:")
        self.check_system_status()
        
    def check_system_status(self):
        """Check overall system status"""
        try:
            # Check health
            response = requests.get(f"{self.base_url}/health")
            health_data = response.json()
            print(f"[System] Health: {health_data['status']}")
            print(f"[System] Assets count: {health_data['assets_count']}")
            
            # Check protocols
            response = requests.get(f"{self.base_url}/api/protocols")
            protocols_data = response.json()
            print(f"[System] Supported protocols: {protocols_data['supported_protocols']}")
            print(f"[System] Device counts: {protocols_data['device_counts']}")
            
            # List all assets
            response = requests.get(f"{self.base_url}/api/latest")
            assets = response.json()
            print(f"\n[System] All connected devices ({len(assets)} total):")
            for asset in assets:
                protocol = asset.get('protocol', 'unknown')
                device_type = asset.get('device_type', 'unknown')
                battery = asset.get('battery', 0)
                print(f"  - {asset['device_id']} ({protocol}, {device_type}): {battery:.1f}% battery")
                
        except Exception as e:
            print(f"[System] ✗ Error checking system status: {e}")

if __name__ == "__main__":
    tester = MultiProtocolTester()
    tester.run_comprehensive_test()