# devices/advanced_simulator.py
import os
import time
import json
import random
import socket
from enum import Enum
from datetime import datetime
import paho.mqtt.client as mqtt

class DeviceType(Enum):
    TRUCK = "truck"
    DRONE = "drone"
    SENSOR_NODE = "sensor"
    WEARABLE = "wearable"

class AdvancedSimulator:
    def __init__(self, device_type: DeviceType, device_id=None):
        self.device_type = device_type
        self.device_id = device_id or f"{device_type.value}-{socket.gethostname()}"
        
        # Device-specific initial states
        if device_type == DeviceType.TRUCK:
            self.lat = float(os.getenv("INIT_LAT", 34.890000))
            self.lon = float(os.getenv("INIT_LON", -1.320000))
            self.battery = float(os.getenv("INIT_BATTERY", random.uniform(60, 100)))
            self.temp = float(os.getenv("INIT_TEMP", random.uniform(24, 32)))
            self.fuel_level = random.uniform(20, 100)
            self.engine_hours = random.randint(1000, 50000)
            
        elif device_type == DeviceType.DRONE:
            self.lat = float(os.getenv("INIT_LAT", 34.890000))
            self.lon = float(os.getenv("INIT_LON", -1.320000))
            self.battery = float(os.getenv("INIT_BATTERY", random.uniform(60, 100)))
            self.temp = float(os.getenv("INIT_TEMP", random.uniform(24, 32)))
            self.altitude = random.uniform(50, 500)
            self.airspeed = random.uniform(0, 50)
            
        elif device_type == DeviceType.SENSOR_NODE:
            self.lat = float(os.getenv("INIT_LAT", 34.890000))
            self.lon = float(os.getenv("INIT_LON", -1.320000))
            self.battery = float(os.getenv("INIT_BATTERY", random.uniform(80, 100)))  # Slower drain
            self.temp = float(os.getenv("INIT_TEMP", random.uniform(20, 30)))
            self.humidity = random.uniform(30, 80)
            
        elif device_type == DeviceType.WEARABLE:
            self.lat = float(os.getenv("INIT_LAT", 34.890000))
            self.lon = float(os.getenv("INIT_LON", -1.320000))
            self.battery = float(os.getenv("INIT_BATTERY", random.uniform(40, 100)))
            self.temp = float(os.getenv("INIT_TEMP", random.uniform(35, 38)))  # Body temp
            self.heart_rate = random.randint(60, 100)
            
        # MQTT setup
        self.broker = os.getenv("MQTT_BROKER", "broker")
        self.port = int(os.getenv("MQTT_PORT", "1883"))
        self.client = mqtt.Client(client_id=self.device_id)
        
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            print(f"[{self.device_id}] Connected to {self.broker}:{self.port}")
            return True
        except Exception as e:
            print(f"[{self.device_id}] Connection failed: {e}")
            return False

    def simulate_gps_with_error(self, base_lat, base_lon):
        """Simulate GPS inaccuracy based on device type"""
        if self.device_type == DeviceType.TRUCK:
            error_range = 0.0001  # ~11 meters - good GPS
        elif self.device_type == DeviceType.DRONE:
            error_range = 0.001   # ~111 meters - less accurate
        elif self.device_type == DeviceType.SENSOR_NODE:
            error_range = 0.0005  # ~55 meters - moderate
        else:  # WEARABLE
            error_range = 0.0003  # ~33 meters - consumer GPS
            
        lat = base_lat + random.uniform(-error_range, error_range)
        lon = base_lon + random.uniform(-error_range, error_range)
        return lat, lon

    def read_sensor_data(self):
        """Read device-specific sensor data"""
        if self.device_type == DeviceType.TRUCK:
            return {
                "engine_temp": random.uniform(80, 110),
                "fuel_level": max(0, self.fuel_level),
                "odometer": self.engine_hours,
                "rpm": random.randint(800, 3000),
                "load_capacity": random.uniform(0, 100)
            }
        elif self.device_type == DeviceType.DRONE:
            return {
                "altitude": max(0, self.altitude),
                "airspeed": self.airspeed,
                "camera_status": random.choice(["ON", "OFF"]),
                "gimbal_pitch": random.uniform(-90, 90),
                "flight_mode": random.choice(["AUTO", "MANUAL", "GUIDED"])
            }
        elif self.device_type == DeviceType.SENSOR_NODE:
            return {
                "humidity": max(0, min(100, self.humidity)),
                "air_quality": random.uniform(0, 500),  # ppm
                "noise_level": random.uniform(30, 100),  # dB
                "vibration": random.uniform(0, 10)  # mm/s
            }
        elif self.device_type == DeviceType.WEARABLE:
            return {
                "heart_rate": max(60, min(180, self.heart_rate)),
                "steps": random.randint(0, 20000),
                "calories": random.randint(1500, 3000),
                "activity": random.choice(["WALKING", "RUNNING", "RESTING"])
            }

    def update_device_state(self):
        """Update device state based on device type"""
        # Common updates
        base_lat, base_lon = 34.89, -1.32
        
        if self.device_type == DeviceType.TRUCK:
            self.lat += random.uniform(-0.001, 0.001)
            self.lon += random.uniform(-0.001, 0.001)
            self.battery = max(0, self.battery - random.uniform(0.05, 0.2))
            self.temp += random.uniform(-0.5, 0.5)
            self.fuel_level = max(0, self.fuel_level - random.uniform(0.1, 0.5))
            self.engine_hours += 1
            
        elif self.device_type == DeviceType.DRONE:
            self.lat += random.uniform(-0.005, 0.005)
            self.lon += random.uniform(-0.005, 0.005)
            self.battery = max(0, self.battery - random.uniform(0.1, 0.8))  # Faster drain
            self.temp += random.uniform(-1, 1)
            self.altitude = max(0, self.altitude + random.uniform(-20, 20))
            self.airspeed = random.uniform(0, 50)
            
        elif self.device_type == DeviceType.SENSOR_NODE:
            # Sensor nodes move very little
            self.lat += random.uniform(-0.0001, 0.0001)
            self.lon += random.uniform(-0.0001, 0.0001)
            self.battery = max(0, self.battery - random.uniform(0.01, 0.05))  # Slow drain
            self.temp += random.uniform(-2, 2)
            self.humidity += random.uniform(-10, 10)
            
        elif self.device_type == DeviceType.WEARABLE:
            self.lat += random.uniform(-0.0005, 0.0005)
            self.lon += random.uniform(-0.0005, 0.0005)
            self.battery = max(0, self.battery - random.uniform(0.05, 0.3))
            self.temp = random.uniform(35, 38)  # Normal body temp range
            self.heart_rate = random.randint(60, 120)

    def get_status(self):
        """Determine device status based on conditions"""
        if self.battery <= 10:
            return "CRITICAL_BATTERY"
        elif self.battery <= 20:
            return "LOW_BATTERY"
        elif self.device_type == DeviceType.TRUCK and self.fuel_level <= 10:
            return "LOW_FUEL"
        elif self.device_type == DeviceType.DRONE and self.altitude <= 10:
            return "LOW_ALTITUDE"
        else:
            return "OK"

    def generate_payload(self):
        """Generate telemetry payload"""
        lat, lon = self.simulate_gps_with_error(self.lat, self.lon)
        
        payload = {
            "device_id": self.device_id,
            "device_type": self.device_type.value,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "battery": round(self.battery, 2),
            "temperature": round(self.temp, 2),
            "status": self.get_status(),
            "sensor_data": self.read_sensor_data(),
            "protocol": "mqtt",
            "signal_strength": random.randint(-120, -50)
        }
        
        return payload

    def simulate_step(self):
        """Perform one simulation step"""
        self.update_device_state()
        payload = self.generate_payload()
        topic = f"fleet/{self.device_id}/telemetry"
        
        try:
            self.client.publish(topic, json.dumps(payload))
            print(f"[{self.device_id}] -> {topic} : {payload['device_type']} - Batt: {payload['battery']}%")
        except Exception as e:
            print(f"[{self.device_id}] Publish failed: {e}")

def main():
    # Get device type from environment or random
    device_type_str = os.getenv("DEVICE_TYPE", "random")
    
    if device_type_str == "random":
        device_type = random.choice(list(DeviceType))
    else:
        try:
            device_type = DeviceType(device_type_str.lower())
        except ValueError:
            device_type = DeviceType.TRUCK
    
    # Create and run simulator
    simulator = AdvancedSimulator(device_type)
    
    if simulator.connect():
        interval = float(os.getenv("PUB_INTERVAL", "5"))
        print(f"[{simulator.device_id}] Starting {device_type.value} simulator, interval: {interval}s")
        
        try:
            while True:
                simulator.simulate_step()
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"[{simulator.device_id}] Stopping...")
    else:
        print(f"[{simulator.device_id}] Failed to start")

if __name__ == '__main__':
    main()