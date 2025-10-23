# virtual-fleet-tracking/devices/device_simulator/geofence_simulator.py
import time
import threading
from managed_device import ManagedDevice

class GeofenceSimulator:
    def __init__(self):
        self.devices = []
        self.running = False
        
    def create_geofence_devices(self):
        """Create devices with different movement patterns and geofences"""
        base_lat, base_lon = 34.89, -1.32
        
        # Stationary device with tight geofence
        stationary_device = ManagedDevice("geo-stationary-001", "sensor", "mqtt")
        stationary_device.set_movement_pattern("stationary")
        self.devices.append(stationary_device)
        
        # Random movement device with medium geofence
        random_device = ManagedDevice("geo-random-001", "drone", "mqtt")
        random_device.set_movement_pattern("random", speed=0.002, range=0.02)
        self.devices.append(random_device)
        
        # Circular movement device
        circular_device = ManagedDevice("geo-circular-001", "truck", "http")
        circular_device.set_movement_pattern("circular", speed=0.001, range=0.015)
        self.devices.append(circular_device)
        
        # Linear movement device (will breach geofence)
        linear_device = ManagedDevice("geo-linear-001", "wearable", "http")
        linear_device.set_movement_pattern("linear", speed=0.003, angle=45, range=0.03)
        self.devices.append(linear_device)
        
    def setup_geofences(self):
        """Setup geofences for all devices"""
        base_lat, base_lon = 34.89, -1.32
        
        # Tight geofence for stationary device
        self.devices[0].set_geofence(base_lat, base_lon, 0.5, "Stationary Zone")
        
        # Medium geofence for random device
        self.devices[1].set_geofence(base_lat, base_lon, 1.5, "Random Movement Zone")
        
        # Circular geofence
        self.devices[2].set_geofence(base_lat, base_lon, 2.0, "Circular Route")
        
        # Small geofence that linear device will breach
        self.devices[3].set_geofence(base_lat, base_lon, 1.0, "Restricted Area")
        
    def start_devices(self):
        """Start all devices"""
        print("🚀 Starting Geofence Simulation")
        print("=" * 50)
        
        for device in self.devices:
            if device.register_with_backend() and device.connect():
                device.fetch_config()
                print(f"✅ {device.device_id} ready - Pattern: {device.movement_pattern}")
        
        # Setup geofences after devices are registered
        time.sleep(2)
        self.setup_geofences()
        
        print("\n🎯 Geofences configured:")
        for device in self.devices:
            print(f"  - {device.device_id}: {device.movement_pattern} movement")
        
        # Start telemetry in separate threads
        self.running = True
        threads = []
        
        for device in self.devices:
            thread = threading.Thread(
                target=self._device_loop,
                args=(device,),
                daemon=True
            )
            threads.append(thread)
            thread.start()
        
        print("\n📍 Devices are now moving and will trigger geofence alerts!")
        print("   Watch the backend logs for geofence breach alerts...")
        print("   Press Ctrl+C to stop simulation")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def _device_loop(self, device):
        """Run device telemetry loop"""
        try:
            while self.running:
                device.send_telemetry()
                time.sleep(device.config.get("telemetry_interval", 10))
        except Exception as e:
            print(f"[{device.device_id}] Error: {e}")
    
    def stop(self):
        """Stop simulation"""
        print("\n🛑 Stopping geofence simulation...")
        self.running = False
        for device in self.devices:
            device.stop()

def main():
    simulator = GeofenceSimulator()
    simulator.create_geofence_devices()
    simulator.start_devices()

if __name__ == "__main__":
    main()