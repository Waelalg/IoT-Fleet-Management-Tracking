# virtual-fleet-tracking/backend/industrial_protocols.py
import logging
from datetime import datetime
from enum import Enum

class IndustrialProtocol(Enum):
    OPCUA = "opcua"
    MODBUS = "modbus"
    LORAWAN = "lorawan"

class LoRaWANHandler:
    def __init__(self):
        self.devices = {}
        self.uplink_callback = None
        print("📶 LoRaWAN Handler Initialized (Simulation Mode)")
        
    def register_device(self, dev_eui, device_info):
        """Register a LoRaWAN device"""
        self.devices[dev_eui] = {
            **device_info,
            'last_seen': None,
            'signal_strength': 0,
            'data_rate': 'SF7',
            'registered_at': datetime.utcnow().isoformat() + "Z"
        }
        print(f"📶 LoRaWAN Device registered: {dev_eui}")
        return True
    
    def handle_uplink(self, dev_eui, payload, rssi, snr):
        """Simulate LoRaWAN uplink message"""
        if dev_eui not in self.devices:
            print(f"📶 Unknown LoRaWAN device: {dev_eui}")
            return False
        
        try:
            # Simulate decoding payload
            telemetry_data = self._decode_payload(payload)
            
            # Update device info
            self.devices[dev_eui].update({
                'last_seen': datetime.utcnow().isoformat() + "Z",
                'signal_strength': rssi,
                'snr': snr
            })
            
            # Convert to standard telemetry format
            standard_telemetry = {
                'device_id': f"lorawan_{dev_eui}",
                'protocol': 'lorawan',
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'lat': telemetry_data.get('lat', 34.89),
                'lon': telemetry_data.get('lon', -1.32),
                'battery': telemetry_data.get('battery', 85),
                'temperature': telemetry_data.get('temperature', 25),
                'signal_strength': rssi,
                'snr': snr,
                'data_rate': self.devices[dev_eui]['data_rate']
            }
            
            # Callback to main application
            if self.uplink_callback:
                self.uplink_callback(standard_telemetry)
                
            print(f"📶 LoRaWAN Uplink from {dev_eui}: RSSI={rssi}, Battery={telemetry_data.get('battery', 85)}%")
            return True
            
        except Exception as e:
            logging.error(f"LoRaWAN uplink processing failed: {e}")
            return False
    
    def send_downlink(self, dev_eui, command):
        """Send downlink command to LoRaWAN device"""
        if dev_eui not in self.devices:
            print(f"📶 Device not found: {dev_eui}")
            return False
        
        try:
            print(f"📶 LoRaWAN Downlink to {dev_eui}: {command}")
            # Simulate successful transmission
            return True
            
        except Exception as e:
            logging.error(f"LoRaWAN downlink failed: {e}")
            return False
    
    def _decode_payload(self, payload_hex):
        """Simulate payload decoding"""
        # Return simulated telemetry data
        return {
            'lat': 34.89 + (hash(payload_hex) % 100) / 10000,  # Small variation
            'lon': -1.32 + (hash(payload_hex) % 100) / 10000,
            'battery': 70 + (hash(payload_hex) % 30),  # 70-100%
            'temperature': 20 + (hash(payload_hex) % 15)  # 20-35°C
        }

class OPCUASimulator:
    def __init__(self):
        self.devices = {}
        print("🔧 OPC-UA Simulator Initialized")
    
    async def update_device_telemetry(self, device_id, telemetry_data):
        """Simulate OPC-UA device update"""
        print(f"🔧 OPC-UA Update for {device_id}: {telemetry_data.get('battery', 0)}%")
        return True

class ModbusSimulator:
    def __init__(self):
        self.devices = {}
        print("🔧 Modbus Simulator Initialized")
    
    def update_device_data(self, device_id, telemetry_data):
        """Simulate Modbus device update"""
        print(f"🔧 Modbus Update for {device_id}: Temp={telemetry_data.get('temperature', 0)}°C")
        return True

class IndustrialProtocolManager:
    def __init__(self, telemetry_callback, alert_callback):
        self.telemetry_callback = telemetry_callback
        self.alert_callback = alert_callback
        
        # Initialize simulators (no external dependencies needed)
        self.protocols = {
            'opcua': OPCUASimulator(),
            'modbus': ModbusSimulator(),
            'lorawan': LoRaWANHandler()
        }
        
        # Set callback for LoRaWAN
        self.protocols['lorawan'].uplink_callback = telemetry_callback
        
        print("🏭 Industrial Protocols Initialized (Simulation Mode)")
        print("   - OPC-UA: Simulator")
        print("   - Modbus: Simulator") 
        print("   - LoRaWAN: Functional")
    
    def handle_telemetry(self, device_id, telemetry_data, protocol):
        """Route telemetry to appropriate industrial protocol"""
        if protocol == IndustrialProtocol.OPCUA.value:
            # Run async function in background
            import asyncio
            asyncio.create_task(
                self.protocols['opcua'].update_device_telemetry(device_id, telemetry_data)
            )
        
        elif protocol == IndustrialProtocol.MODBUS.value:
            self.protocols['modbus'].update_device_data(device_id, telemetry_data)
        
        elif protocol == IndustrialProtocol.LORAWAN.value:
            # LoRaWAN devices are handled via uplink
            pass
    
    def send_command(self, device_id, command, protocol):
        """Send command via industrial protocol"""
        if protocol == IndustrialProtocol.LORAWAN.value:
            # Extract DevEUI from device_id
            dev_eui = device_id.replace('lorawan_', '')
            return self.protocols['lorawan'].send_downlink(dev_eui, command)
        
        return False

# Global industrial protocol manager
industrial_manager = None

def initialize_industrial_protocols(telemetry_callback, alert_callback):
    global industrial_manager
    industrial_manager = IndustrialProtocolManager(telemetry_callback, alert_callback)
    return industrial_manager