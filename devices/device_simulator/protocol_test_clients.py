# devices/protocol_test_clients.py
import json
import time
import random
import socket
from datetime import datetime
import paho.mqtt.client as mqtt
import aiohttp
import asyncio

class MultiProtocolTester:
    def __init__(self, device_id, device_type="truck"):
        self.device_id = device_id
        self.device_type = device_type
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
                "signal_strength": random.randint(-120, -50)
            }
        }

class MQTTTester(MultiProtocolTester):
    def __init__(self, device_id, device_type="truck"):
        super().__init__(device_id, device_type)
        self.client = mqtt.Client(client_id=device_id)
        self.broker = "broker"
        self.port = 1883
        
    def connect(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            print(f"[MQTT {self.device_id}] Connected")
            return True
        except Exception as e:
            print(f"[MQTT {self.device_id}] Connection failed: {e}")
            return False
            
    def send_telemetry(self):
        payload = self.generate_payload()
        topic = f"fleet/{self.device_id}/telemetry"
        self.client.publish(topic, json.dumps(payload))
        print(f"[MQTT {self.device_id}] Sent telemetry")

class HTTPTester(MultiProtocolTester):
    def __init__(self, device_id, device_type="truck"):
        super().__init__(device_id, device_type)
        self.url = "http://backend:5002"
        
    async def send_telemetry(self):
        payload = self.generate_payload()
        try:
            async with aiohttp.ClientSession() as session:
                # FIX: Use correct endpoint /http/telemetry instead of /telemetry
                async with session.post(f"{self.url}/http/telemetry", json=payload) as response:
                    if response.status == 200:
                        print(f"[HTTP {self.device_id}] Sent telemetry")
                    else:
                        print(f"[HTTP {self.device_id}] Failed: {response.status}")
        except Exception as e:
            print(f"[HTTP {self.device_id}] Error: {e}")

class CoAPTester(MultiProtocolTester):
    def __init__(self, device_id, device_type="truck"):
        super().__init__(device_id, device_type)
        self.url = "http://backend:5002"  # Use HTTP bridge for CoAP
        
    async def send_telemetry(self):
        payload = self.generate_payload()
        try:
            # FIX: Use HTTP bridge for CoAP since backend doesn't have native CoAP server
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.url}/coap/telemetry", json=payload) as response:
                    if response.status == 200:
                        print(f"[CoAP {self.device_id}] Sent telemetry via HTTP bridge")
                    else:
                        print(f"[CoAP {self.device_id}] Failed: {response.status}")
        except Exception as e:
            print(f"[CoAP {self.device_id}] Error: {e}")

def test_all_protocols():
    """Test all protocols with different devices"""
    devices = [
        ("mqtt-truck-1", "truck", "mqtt"),
        ("http-drone-1", "drone", "http"), 
        ("coap-sensor-1", "sensor", "coap"),
        ("mqtt-wearable-1", "wearable", "mqtt")
    ]
    
    # Test MQTT
    mqtt_testers = []
    for device_id, device_type, protocol in devices:
        if protocol == "mqtt":
            tester = MQTTTester(device_id, device_type)
            if tester.connect():
                mqtt_testers.append(tester)
    
    # Send MQTT telemetry
    for tester in mqtt_testers:
        tester.send_telemetry()
    
    # Test HTTP and CoAP (async)
    async def test_async_protocols():
        http_tester = HTTPTester("http-test-1", "truck")
        coap_tester = CoAPTester("coap-test-1", "sensor")
        
        await http_tester.send_telemetry()
        await coap_tester.send_telemetry()
    
    asyncio.run(test_async_protocols())

if __name__ == "__main__":
    test_all_protocols()