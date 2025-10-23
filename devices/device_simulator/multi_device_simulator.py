# devices/device_simulator/multi_device_simulator.py
import asyncio
import threading
import time
import random
from datetime import datetime
from advanced_simulator import AdvancedSimulator, DeviceType
from http_device import HTTPDevice
from coap_device import CoAPDevice
import paho.mqtt.client as mqtt
import json

class MultiDeviceMultiProtocolSimulator:
    def __init__(self):
        self.devices = []
        self.running = False
        
    def create_mqtt_devices(self):
        """Create MQTT devices of different types"""
        mqtt_devices = [
            ("mqtt-truck-001", DeviceType.TRUCK, 5),
            ("mqtt-drone-001", DeviceType.DRONE, 3),
            ("mqtt-sensor-001", DeviceType.SENSOR_NODE, 10),
            ("mqtt-wearable-001", DeviceType.WEARABLE, 8)
        ]
        
        for device_id, device_type, interval in mqtt_devices:
            simulator = AdvancedSimulator(device_type, device_id)
            if simulator.connect():
                self.devices.append(("mqtt", device_id, simulator, interval))
                print(f"[MQTT] Created {device_type.value}: {device_id}")
    
    def create_http_devices(self):
        """Create HTTP devices of different types"""
        http_devices = [
            ("http-truck-001", "truck", 6),
            ("http-drone-001", "drone", 4),
            ("http-sensor-001", "sensor", 12),
            ("http-wearable-001", "wearable", 9)
        ]
        
        for device_id, device_type, interval in http_devices:
            device = HTTPDevice(device_id, device_type)
            self.devices.append(("http", device_id, device, interval))
            print(f"[HTTP] Created {device_type}: {device_id}")
    
    def create_coap_devices(self):
        """Create CoAP devices of different types"""
        coap_devices = [
            ("coap-truck-001", "truck", 15),
            ("coap-sensor-001", "sensor", 25),
            ("coap-wearable-001", "wearable", 20)
        ]
        
        for device_id, device_type, interval in coap_devices:
            device = CoAPDevice(device_id, device_type)
            self.devices.append(("coap", device_id, device, interval))
            print(f"[CoAP] Created {device_type}: {device_id}")
    
    def run_mqtt_device(self, device_id, simulator, interval):
        """Run MQTT device in a separate thread"""
        print(f"[MQTT {device_id}] Starting, interval: {interval}s")
        try:
            while self.running:
                simulator.simulate_step()
                time.sleep(interval)
        except Exception as e:
            print(f"[MQTT {device_id}] Error: {e}")
    
    def run_http_device(self, device_id, device, interval):
        """Run HTTP device in a separate thread"""
        print(f"[HTTP {device_id}] Starting, interval: {interval}s")
        try:
            while self.running:
                device.send_telemetry()
                time.sleep(interval)
        except Exception as e:
            print(f"[HTTP {device_id}] Error: {e}")
    
    async def run_coap_device_async(self, device_id, device, interval):
        """Run CoAP device asynchronously"""
        print(f"[CoAP {device_id}] Starting, interval: {interval}s")
        try:
            while self.running:
                device.send_telemetry()
                await asyncio.sleep(interval)
        except Exception as e:
            print(f"[CoAP {device_id}] Error: {e}")
    
    def start(self):
        """Start all devices"""
        print("🚀 Starting Multi-Device Multi-Protocol Simulation")
        print("=" * 50)
        
        # Create devices
        self.create_mqtt_devices()
        self.create_http_devices()
        self.create_coap_devices()
        
        print(f"\n📡 Total devices created: {len(self.devices)}")
        print("Protocol breakdown:")
        protocols = {}
        for protocol, device_id, _, _ in self.devices:
            protocols[protocol] = protocols.get(protocol, 0) + 1
        for protocol, count in protocols.items():
            print(f"  - {protocol.upper()}: {count} devices")
        
        # Start simulation
        self.running = True
        threads = []
        
        # Start MQTT and HTTP devices in threads
        for protocol, device_id, device, interval in self.devices:
            if protocol == "mqtt":
                thread = threading.Thread(
                    target=self.run_mqtt_device, 
                    args=(device_id, device, interval),
                    daemon=True
                )
                threads.append(thread)
            elif protocol == "http":
                thread = threading.Thread(
                    target=self.run_http_device, 
                    args=(device_id, device, interval),
                    daemon=True
                )
                threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Run CoAP devices asynchronously
        async def run_all_coap():
            coap_tasks = []
            for protocol, device_id, device, interval in self.devices:
                if protocol == "coap":
                    task = asyncio.create_task(
                        self.run_coap_device_async(device_id, device, interval)
                    )
                    coap_tasks.append(task)
            
            if coap_tasks:
                await asyncio.gather(*coap_tasks)
        
        # Start the simulation
        try:
            print("\n🎯 Simulation running! Press Ctrl+C to stop...")
            asyncio.run(run_all_coap())
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop all devices"""
        print("\n🛑 Stopping simulation...")
        self.running = False

def main():
    simulator = MultiDeviceMultiProtocolSimulator()
    simulator.start()

if __name__ == "__main__":
    main()