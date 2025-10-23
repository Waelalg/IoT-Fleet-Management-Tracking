import time
import json
import random
import threading
import math
from datetime import datetime
import paho.mqtt.client as mqtt
import requests

class ManagedDevice:
    def __init__(self, device_id, device_type, protocol="mqtt"):
        self.device_id = device_id
        self.device_type = device_type
        self.protocol = protocol
        self.firmware_version = "1.2.0"
        self.capabilities = ["telemetry", "alerts", "config_update", "remote_commands", "geofencing"]
        
        # Device state
        self.config = {
            "telemetry_interval": 10,
            "heartbeat_interval": 60,
            "alert_thresholds": {
                "battery": 20,
                "temperature": 40
            }
        }
        
        # Movement simulation
        self.base_lat = 34.89
        self.base_lon = -1.32
        self.current_lat = self.base_lat
        self.current_lon = self.base_lon
        self.movement_pattern = "stationary"
        self.movement_speed = 0.001
        self.movement_angle = 0
        self.movement_range = 0.01
        
        self.pending_commands = []
        self.running = False
        
        # MQTT setup
        if protocol == "mqtt":
            self.client = mqtt.Client(client_id=device_id)
            self.broker = "broker"
            self.port = 1883
        
        # HTTP setup
        self.backend_url = "http://backend:5002"
        
        # Device-specific initial state
        self.battery = random.uniform(80, 100)
        self.temperature = random.uniform(20, 30)
        self.status = "OK"
        
    def set_movement_pattern(self, pattern, **kwargs):
        """Set device movement pattern"""
        self.movement_pattern = pattern
        if pattern == "circular":
            self.movement_speed = kwargs.get('speed', 0.001)
            self.movement_range = kwargs.get('range', 0.01)
        elif pattern == "random":
            self.movement_speed = kwargs.get('speed', 0.001)
            self.movement_range = kwargs.get('range', 0.02)
        elif pattern == "linear":
            self.movement_speed = kwargs.get('speed', 0.002)
            self.movement_angle = kwargs.get('angle', 45)
        elif pattern == "stationary":
            self.current_lat = self.base_lat
            self.current_lon = self.base_lon
            
        print(f"[{self.device_id}] Movement pattern: {pattern}")

    def update_position(self):
        """Update device position based on movement pattern"""
        if self.movement_pattern == "stationary":
            self.current_lat = self.base_lat + random.uniform(-0.0001, 0.0001)
            self.current_lon = self.base_lon + random.uniform(-0.0001, 0.0001)
            
        elif self.movement_pattern == "random":
            self.current_lat += random.uniform(-self.movement_speed, self.movement_speed)
            self.current_lon += random.uniform(-self.movement_speed, self.movement_speed)
            
            self.current_lat = max(self.base_lat - self.movement_range, 
                                 min(self.base_lat + self.movement_range, self.current_lat))
            self.current_lon = max(self.base_lon - self.movement_range, 
                                 min(self.base_lon + self.movement_range, self.current_lon))
                                 
        elif self.movement_pattern == "circular":
            self.movement_angle = (self.movement_angle + 5) % 360
            angle_rad = math.radians(self.movement_angle)
            
            self.current_lat = self.base_lat + self.movement_range * math.cos(angle_rad)
            self.current_lon = self.base_lon + self.movement_range * math.sin(angle_rad)
            
        elif self.movement_pattern == "linear":
            angle_rad = math.radians(self.movement_angle)
            
            self.current_lat += self.movement_speed * math.cos(angle_rad)
            self.current_lon += self.movement_speed * math.sin(angle_rad)
            
            distance_from_base = math.sqrt(
                (self.current_lat - self.base_lat)**2 + 
                (self.current_lon - self.base_lon)**2
            )
            
            if distance_from_base > self.movement_range:
                self.movement_angle = (self.movement_angle + 180) % 360

    def register_with_backend(self):
        """Register device with backend management system"""
        registration_data = {
            "device_type": self.device_type,
            "protocol": self.protocol,
            "firmware_version": self.firmware_version,
            "capabilities": self.capabilities,
            "telemetry_interval": self.config["telemetry_interval"]
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/api/devices/{self.device_id}",
                json=registration_data
            )
            if response.status_code == 200:
                print(f"[{self.device_id}] ✅ Registered with backend")
                return True
            else:
                print(f"[{self.device_id}] ❌ Registration failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[{self.device_id}] ❌ Registration error: {e}")
            return False
    
    def fetch_config(self):
        """Fetch configuration from backend"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/devices/{self.device_id}/config"
            )
            if response.status_code == 200:
                new_config = response.json()
                self.config.update(new_config)
                print(f"[{self.device_id}] 🔧 Config updated")
                return True
        except Exception as e:
            print(f"[{self.device_id}] ❌ Config fetch error: {e}")
        return False
    
    def check_commands(self):
        """Check for pending commands from backend"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/devices/{self.device_id}/commands"
            )
            if response.status_code == 200:
                commands = response.json()
                for command in commands:
                    if command["status"] == "pending":
                        self.execute_command(command)
        except Exception as e:
            print(f"[{self.device_id}] ❌ Command check error: {e}")
    
    def execute_command(self, command):
        """Execute a remote command"""
        command_id = command["command_id"]
        command_type = command["type"]
        
        print(f"[{self.device_id}] 🎯 Executing command: {command_type}")
        
        try:
            if command_type == "config_update":
                new_config = command.get("config", {})
                self.config.update(new_config)
                print(f"[{self.device_id}] 🔧 Config updated via command")
                
            elif command_type == "reboot":
                print(f"[{self.device_id}] 🔄 Simulating reboot...")
                time.sleep(2)
                print(f"[{self.device_id}] ✅ Reboot complete")
                
            elif command_type == "update_interval":
                new_interval = command.get("parameters", {}).get("interval", 10)
                self.config["telemetry_interval"] = new_interval
                print(f"[{self.device_id}] ⏱️ Telemetry interval updated to {new_interval}s")
                
            elif command_type == "diagnostic":
                print(f"[{self.device_id}] 📊 Running diagnostic...")
                time.sleep(1)
                
            # Acknowledge command
            requests.post(
                f"{self.backend_url}/api/devices/{self.device_id}/commands/{command_id}/ack"
            )
            
        except Exception as e:
            print(f"[{self.device_id}] ❌ Command execution error: {e}")
    
    def generate_telemetry(self):
        """Generate telemetry data with updated position"""
        self.update_position()
        
        battery_drain = 0.05
        if self.movement_pattern != "stationary":
            battery_drain = 0.1 + (0.1 * self.movement_speed / 0.001)
            
        self.battery = max(0, self.battery - random.uniform(battery_drain * 0.5, battery_drain * 1.5))
        self.temperature += random.uniform(-0.5, 0.5)
        
        if self.battery <= self.config["alert_thresholds"]["battery"]:
            self.status = "LOW_BATTERY"
        elif self.temperature >= self.config["alert_thresholds"]["temperature"]:
            self.status = "HIGH_TEMP"
        else:
            self.status = "OK"
        
        payload = {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "lat": round(self.current_lat, 6),
            "lon": round(self.current_lon, 6),
            "battery": round(self.battery, 2),
            "temperature": round(self.temperature, 2),
            "status": self.status,
            "protocol": self.protocol,
            "firmware_version": self.firmware_version,
            "config": self.config,
            "movement_pattern": self.movement_pattern,
            "signal_strength": random.randint(-120, -50)
        }
        
        return payload

    def send_telemetry(self):
        """Send telemetry data via configured protocol"""
        payload = self.generate_telemetry()
        
        if self.protocol == "mqtt":
            topic = f"fleet/{self.device_id}/telemetry"
            self.client.publish(topic, json.dumps(payload))
            print(f"[{self.device_id}] 📡 MQTT Telemetry: Battery {payload['battery']}%")
            
        elif self.protocol == "http":
            try:
                response = requests.post(
                    f"{self.backend_url}/http/telemetry",
                    json=payload,
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"[{self.device_id}] 📡 HTTP Telemetry: Battery {payload['battery']}%")
                else:
                    print(f"[{self.device_id}] ❌ HTTP Telemetry failed: {response.status_code}")
            except Exception as e:
                print(f"[{self.device_id}] ❌ HTTP Telemetry error: {e}")
    
    def set_geofence(self, center_lat, center_lon, radius_km, name=None):
        """Set geofence for this device"""
        geofence_data = {
            "center_lat": center_lat,
            "center_lon": center_lon,
            "radius_km": radius_km,
            "alert_on_breach": True,
            "alert_on_return": True,
            "name": name or f"Geofence for {self.device_id}"
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/api/devices/{self.device_id}/geofence",
                json=geofence_data
            )
            if response.status_code == 200:
                print(f"[{self.device_id}] ✅ Geofence set: {geofence_data['name']}")
                return True
            else:
                print(f"[{self.device_id}] ❌ Geofence setup failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[{self.device_id}] ❌ Geofence setup error: {e}")
            return False

    def connect(self):
        """Connect device to network"""
        if self.protocol == "mqtt":
            try:
                self.client.connect(self.broker, self.port, 60)
                self.client.loop_start()
                self.client.subscribe(f"fleet/{self.device_id}/commands")
                self.client.on_message = self._on_mqtt_message
                
                print(f"[{self.device_id}] ✅ MQTT Connected")
                return True
            except Exception as e:
                print(f"[{self.device_id}] ❌ MQTT Connection failed: {e}")
                return False
        else:
            print(f"[{self.device_id}] ✅ HTTP Device ready")
            return True
    
    def _on_mqtt_message(self, client, userdata, msg):
        """Handle incoming MQTT messages (commands)"""
        try:
            payload = msg.payload.decode("utf-8")
            command = json.loads(payload)
            self.execute_command(command)
        except Exception as e:
            print(f"[{self.device_id}] ❌ MQTT message error: {e}")
    
    def start(self):
        """Start device operation"""
        if not self.register_with_backend():
            print(f"[{self.device_id}] ❌ Failed to start - registration failed")
            return False
        
        if not self.connect():
            return False
        
        self.fetch_config()
        self.running = True
        
        management_thread = threading.Thread(target=self._management_loop, daemon=True)
        management_thread.start()
        
        print(f"[{self.device_id}] 🚀 Started managed device, interval: {self.config['telemetry_interval']}s")
        try:
            while self.running:
                self.send_telemetry()
                time.sleep(self.config["telemetry_interval"])
        except KeyboardInterrupt:
            self.stop()
    
    def _management_loop(self):
        """Background management tasks"""
        while self.running:
            self.check_commands()
            time.sleep(10)
    
    def stop(self):
        """Stop device operation"""
        self.running = False
        if self.protocol == "mqtt":
            self.client.loop_stop()
        print(f"[{self.device_id}] 🛑 Stopped")