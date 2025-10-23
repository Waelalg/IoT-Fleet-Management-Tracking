# devices/device_simulator/test_managed_devices.py
import time
import threading
from managed_device import ManagedDevice

def start_managed_devices():
    """Start multiple managed devices with different protocols"""
    devices = [
        ManagedDevice("managed-truck-001", "truck", "mqtt"),
        ManagedDevice("managed-drone-001", "drone", "mqtt"),
        ManagedDevice("managed-sensor-001", "sensor", "http"),
        ManagedDevice("managed-wearable-001", "wearable", "http"),
    ]
    
    threads = []
    for device in devices:
        thread = threading.Thread(target=device.start, daemon=True)
        threads.append(thread)
        thread.start()
        time.sleep(1)  # Stagger startup
    
    print("🚀 All managed devices started!")
    print("Use these API endpoints to manage devices:")
    print("  GET  http://localhost:5002/api/devices")
    print("  GET  http://localhost:5002/api/devices/<device_id>")
    print("  PUT  http://localhost:5002/api/devices/<device_id>/config")
    print("  POST http://localhost:5002/api/devices/<device_id>/commands")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all devices...")
        for device in devices:
            device.stop()

if __name__ == "__main__":
    start_managed_devices()