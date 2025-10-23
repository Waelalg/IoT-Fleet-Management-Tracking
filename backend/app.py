# virtual-fleet-tracking/backend/app.py
import os
import time
import json
import threading
import uuid
import math
import asyncio
from datetime import datetime, timedelta
from collections import deque, defaultdict

from flask import Flask, jsonify, request
from flask_cors import CORS

# Import protocol router
from protocol_router import ProtocolRouter, Protocol

# Import edge computing and industrial protocols
from edge_processor import edge_processor, predictive_maintenance
from industrial_protocols import initialize_industrial_protocols, IndustrialProtocol

# Config from environment
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "5002"))

# In-memory stores
assets = {}
telemetry = defaultdict(lambda: deque(maxlen=500))
alerts = deque(maxlen=1000)
device_registry = {}  # device_id -> device_info
device_configs = {}   # device_id -> configuration
device_commands = {}  # device_id -> pending_commands
geofences = {}  # device_id -> geofence_config
device_geofence_state = {}  # device_id -> current_state

# Edge computing and industrial protocols
edge_insights = {}  # device_id -> edge analytics
maintenance_predictions = {}  # device_id -> maintenance data

# Flask app
app = Flask(__name__)
CORS(app)

# Protocol router
protocol_router = None
industrial_manager = None

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def is_device_online(device_id):
    """Check if device is online based on last telemetry"""
    if device_id not in telemetry or not telemetry[device_id]:
        return False
    
    latest_telemetry = list(telemetry[device_id])[-1]
    last_seen_str = latest_telemetry.get('timestamp')
    
    if not last_seen_str:
        return False
    
    try:
        # Remove the 'Z' and parse
        if last_seen_str.endswith('Z'):
            last_seen_str = last_seen_str[:-1]
        last_seen = datetime.fromisoformat(last_seen_str)
        # Consider device online if seen in last 5 minutes
        return datetime.utcnow() - last_seen < timedelta(minutes=5)
    except:
        return False

def check_geofence_breach(device_id, current_lat, current_lon):
    """Check if device has breached its geofence"""
    if device_id not in geofences:
        return None
    
    geofence = geofences[device_id]
    center_lat = geofence["center_lat"]
    center_lon = geofence["center_lon"]
    radius_km = geofence["radius_km"]
    
    distance = calculate_distance(center_lat, center_lon, current_lat, current_lon)
    is_inside = distance <= radius_km
    
    previous_state = device_geofence_state.get(device_id, "inside")
    current_state = "inside" if is_inside else "outside"
    
    # State changed
    if previous_state != current_state:
        device_geofence_state[device_id] = current_state
        
        if current_state == "outside" and geofence["alert_on_breach"]:
            return {
                "type": "GEOFENCE_BREACH",
                "device_id": device_id,
                "previous_state": previous_state,
                "current_state": current_state,
                "distance_from_center_km": round(distance, 2),
                "geofence_name": geofence["name"],
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        elif current_state == "inside" and geofence["alert_on_return"]:
            return {
                "type": "GEOFENCE_RETURN",
                "device_id": device_id,
                "previous_state": previous_state,
                "current_state": current_state,
                "distance_from_center_km": round(distance, 2),
                "geofence_name": geofence["name"],
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
    
    return None

def enhanced_handle_telemetry(data):
    """Enhanced telemetry handler with edge computing and industrial protocols"""
    device_id = data.get("device_id") or data.get("id", "unknown")
    protocol = data.get("protocol", "unknown")
    
    # Edge computing: Anomaly detection
    is_anomaly = edge_processor.detect_anomalies(device_id, data)
    
    if is_anomaly:
        print(f"🚨 Edge Anomaly Detected for {device_id}")
    
    # Edge computing: Data compression simulation
    previous_data = list(telemetry.get(device_id, deque(maxlen=1)))[-1] if telemetry.get(device_id) else None
    compressed_data, should_process = edge_processor.compress_telemetry(device_id, data, previous_data)
    
    if not should_process and previous_data:
        print(f"📦 Edge compression: Skipping similar data for {device_id}")
        # Still update edge insights but don't process full telemetry
        return
    
    # Use compressed data if available, otherwise original data
    processed_data = compressed_data if compressed_data else data
    
    # Store edge insights
    edge_insights[device_id] = {
        "last_processed": datetime.utcnow().isoformat() + "Z",
        "anomaly_detected": is_anomaly,
        "data_compressed": compressed_data is not None,
        "compression_ratio": len(json.dumps(compressed_data)) / len(json.dumps(data)) if compressed_data else 1.0
    }
    
    # Continue with original processing
    original_handle_telemetry(processed_data)

def original_handle_telemetry(data):
    """Original telemetry handling logic with industrial protocol integration"""
    device_id = data.get("device_id") or data.get("id", "unknown")
    protocol = data.get("protocol", "unknown")
    
    # Auto-register device if not already registered
    if device_id not in device_registry:
        device_registry[device_id] = {
            "device_type": data.get("device_type", "unknown"),
            "protocol": protocol,
            "firmware_version": "unknown",
            "capabilities": [],
            "registered_at": datetime.utcnow().isoformat() + "Z",
            "status": "active"
        }
        print(f"[Device Management] Auto-registered device: {device_id}")
    
    # Get current position
    current_lat = float(data.get("lat", 0.0))
    current_lon = float(data.get("lon", 0.0))
    
    # Check geofence breach
    geofence_alert = check_geofence_breach(device_id, current_lat, current_lon)
    if geofence_alert:
        print(f"[Geofence Alert] {device_id}: {geofence_alert['type']}")
        # Add to alerts
        alerts.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "device_id": device_id,
            "device_type": data.get("device_type", "unknown"),
            "type": geofence_alert["type"],
            "detail": f"Device moved {geofence_alert['current_state']} geofence '{geofence_alert['geofence_name']}'",
            "distance_km": geofence_alert["distance_from_center_km"],
            "protocol": protocol
        })
    
    # Canonicalize and store
    record = {
        "device_id": device_id,
        "timestamp": data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
        "lat": current_lat,
        "lon": current_lon,
        "battery": float(data.get("battery", 0.0)),
        "temperature": float(data.get("temperature", 0.0)),
        "status": data.get("status", "OK"),
        "device_type": data.get("device_type", "unknown"),
        "sensor_data": data.get("sensor_data", {}),
        "signal_strength": data.get("signal_strength", 0),
        "protocol": protocol,
        "received_at": data.get("received_at"),
        "geofence_state": device_geofence_state.get(device_id, "unknown"),
        "edge_processed": True,
        "compressed": data.get("compressed", False)
    }

    assets[device_id] = record
    telemetry[device_id].append(record)

    # Predictive maintenance analysis (run every 10 telemetry points)
    device_history = list(telemetry.get(device_id, []))
    if len(device_history) % 10 == 0:  # Run analysis periodically
        maintenance_prediction = predictive_maintenance.analyze_health_trends(device_id, device_history)
        if maintenance_prediction:
            maintenance_predictions[device_id] = maintenance_prediction
            
            # Trigger maintenance alert if health is poor
            if maintenance_prediction["health_score"] < 0.4:
                alerts.append({
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "device_id": device_id,
                    "type": "PREDICTIVE_MAINTENANCE",
                    "detail": f"Device health score: {maintenance_prediction['health_score']:.2f}",
                    "predicted_maintenance": maintenance_prediction["predicted_maintenance_date"],
                    "recommended_actions": maintenance_prediction["recommended_actions"],
                    "protocol": protocol,
                    "severity": "high"
                })
                print(f"🔧 Predictive Maintenance Alert for {device_id}: Health score {maintenance_prediction['health_score']:.2f}")

    # Update industrial protocols
    if industrial_manager:
        industrial_manager.handle_telemetry(device_id, record, protocol)

    print(f"[backend] Received {protocol} telemetry from {device_id} -> Battery: {record['battery']}%")

def handle_alert(data):
    """Handle alert data from any protocol"""
    protocol = data.get("protocol", "unknown")
    print(f"[backend] Received {protocol} alert: {data}")
    
    # Store alert
    alert_record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "device_id": data.get("device_id", "unknown"),
        "device_type": data.get("device_type", "unknown"),
        "type": data.get("type", "UNKNOWN_ALERT"),
        "detail": data.get("detail", ""),
        "protocol": protocol,
        "received_at": data.get("received_at"),
        "severity": data.get("severity", "medium")
    }
    
    alerts.append(alert_record)

# Initialize protocol router and industrial protocols
def init_protocol_router():
    global protocol_router, industrial_manager
    protocol_router = ProtocolRouter(enhanced_handle_telemetry, handle_alert)
    protocol_router.start_all()
    
    # Initialize industrial protocols
    industrial_manager = initialize_industrial_protocols(enhanced_handle_telemetry, handle_alert)
    print("🏭 Industrial Protocols Initialized")

# Start protocol router in background thread
router_thread = threading.Thread(target=init_protocol_router, daemon=True)
router_thread.start()

# ============================================================================
# EDGE COMPUTING & ANALYTICS ROUTES
# ============================================================================

@app.route("/api/edge/insights", methods=["GET"])
def get_edge_insights():
    """Get edge computing insights for all devices"""
    return jsonify(edge_insights)

@app.route("/api/devices/<device_id>/edge", methods=["GET"])
def get_device_edge_insights(device_id):
    """Get edge computing insights for specific device"""
    if device_id not in device_registry:
        return jsonify({"error": "Device not found"}), 404
    
    insights = edge_insights.get(device_id, {})
    prediction = maintenance_predictions.get(device_id, {})
    
    return jsonify({
        "device_id": device_id,
        "edge_insights": insights,
        "predictive_maintenance": prediction,
        "telemetry_count": len(telemetry.get(device_id, [])),
        "anomaly_history": [alert for alert in alerts if alert.get('device_id') == device_id and 'ANOMALY' in alert.get('type', '')]
    })

@app.route("/api/devices/<device_id>/maintenance", methods=["GET"])
def get_device_maintenance(device_id):
    """Get predictive maintenance data for device"""
    if device_id not in device_registry:
        return jsonify({"error": "Device not found"}), 404
    
    prediction = maintenance_predictions.get(device_id)
    
    if not prediction:
        # Generate on-demand if not exists
        device_history = list(telemetry.get(device_id, []))
        if device_history:
            prediction = predictive_maintenance.analyze_health_trends(device_id, device_history)
            if prediction:
                maintenance_predictions[device_id] = prediction
    
    return jsonify({
        "device_id": device_id,
        "predictive_maintenance": prediction,
        "health_score": prediction.get("health_score", 0.0) if prediction else 0.0,
        "battery_degradation": predictive_maintenance._calculate_battery_degradation(list(telemetry.get(device_id, []))) if telemetry.get(device_id) else 0.0
    })

@app.route("/api/analytics/health-scores", methods=["GET"])
def get_health_scores():
    """Get health scores for all devices"""
    scores = {}
    for device_id in device_registry:
        prediction = maintenance_predictions.get(device_id)
        if prediction:
            scores[device_id] = {
                "health_score": prediction["health_score"],
                "maintenance_date": prediction["predicted_maintenance_date"],
                "online": is_device_online(device_id)
            }
        else:
            scores[device_id] = {
                "health_score": 1.0,  # Default perfect health
                "maintenance_date": None,
                "online": is_device_online(device_id)
            }
    
    return jsonify(scores)

# ============================================================================
# INDUSTRIAL PROTOCOL ROUTES
# ============================================================================

@app.route("/api/protocols/industrial", methods=["GET"])
def get_industrial_protocols():
    """Get industrial protocol status and endpoints"""
    if not industrial_manager:
        return jsonify({"error": "Industrial protocols not initialized"}), 500
    
    status = {
        "opcua": {
            "enabled": industrial_manager.protocols['opcua'] is not None,
            "endpoint": "opc.tcp://localhost:4840" if industrial_manager.protocols['opcua'] else None
        },
        "modbus": {
            "enabled": industrial_manager.protocols['modbus'] is not None,
            "endpoint": "localhost:5020" if industrial_manager.protocols['modbus'] else None
        },
        "lorawan": {
            "enabled": industrial_manager.protocols['lorawan'] is not None,
            "devices_registered": len(industrial_manager.protocols['lorawan'].devices) if industrial_manager.protocols['lorawan'] else 0
        }
    }
    
    return jsonify(status)

@app.route("/api/protocols/lorawan/devices", methods=["GET", "POST"])
def lorawan_devices():
    """Manage LoRaWAN devices"""
    if not industrial_manager or not industrial_manager.protocols['lorawan']:
        return jsonify({"error": "LoRaWAN not available"}), 500
    
    if request.method == "GET":
        return jsonify(industrial_manager.protocols['lorawan'].devices)
    
    elif request.method == "POST":
        data = request.get_json()
        if not data or "dev_eui" not in data:
            return jsonify({"error": "DevEUI required"}), 400
        
        industrial_manager.protocols['lorawan'].register_device(data["dev_eui"], data)
        return jsonify({"status": "success", "dev_eui": data["dev_eui"]})

@app.route("/api/protocols/lorawan/<dev_eui>/downlink", methods=["POST"])
def send_lorawan_downlink(dev_eui):
    """Send downlink command to LoRaWAN device"""
    if not industrial_manager or not industrial_manager.protocols['lorawan']:
        return jsonify({"error": "LoRaWAN not available"}), 500
    
    data = request.get_json()
    if not data or "command" not in data:
        return jsonify({"error": "Command required"}), 400
    
    success = industrial_manager.send_command(f"lorawan_{dev_eui}", data, IndustrialProtocol.LORAWAN.value)
    
    return jsonify({
        "status": "success" if success else "failed",
        "dev_eui": dev_eui,
        "command": data["command"]
    })

# ============================================================================
# DEVICE MANAGEMENT ROUTES
# ============================================================================

@app.route("/api/devices", methods=["GET"])
def get_all_devices():
    """Get all registered devices with their status"""
    devices_list = []
    for device_id, device_info in device_registry.items():
        # Get latest telemetry for each device
        latest_telemetry = list(telemetry.get(device_id, deque(maxlen=1)))
        last_seen = latest_telemetry[0].get('timestamp') if latest_telemetry else None
        
        # Get edge insights and maintenance data
        edge_data = edge_insights.get(device_id, {})
        maintenance_data = maintenance_predictions.get(device_id, {})
        
        device_data = {
            "device_id": device_id,
            **device_info,
            "last_seen": last_seen,
            "online": is_device_online(device_id),
            "config": device_configs.get(device_id, {}),
            "pending_commands": device_commands.get(device_id, []),
            "geofence": geofences.get(device_id),
            "geofence_state": device_geofence_state.get(device_id, "unknown"),
            "edge_insights": edge_data,
            "predictive_maintenance": maintenance_data,
            "health_score": maintenance_data.get("health_score", 1.0)
        }
        devices_list.append(device_data)
    
    return jsonify(devices_list)

@app.route("/api/devices/<device_id>", methods=["GET"])
def get_device(device_id):
    """Get specific device details"""
    if device_id not in device_registry:
        return jsonify({"error": "Device not found"}), 404
    
    latest_telemetry = list(telemetry.get(device_id, deque(maxlen=1)))
    last_seen = latest_telemetry[0].get('timestamp') if latest_telemetry else None
    
    # Get edge and maintenance data
    edge_data = edge_insights.get(device_id, {})
    maintenance_data = maintenance_predictions.get(device_id, {})
    
    device_data = {
        "device_id": device_id,
        **device_registry[device_id],
        "last_seen": last_seen,
        "online": is_device_online(device_id),
        "config": device_configs.get(device_id, {}),
        "pending_commands": device_commands.get(device_id, []),
        "geofence": geofences.get(device_id),
        "geofence_state": device_geofence_state.get(device_id, "unknown"),
        "telemetry_history": list(telemetry.get(device_id, []))[-10:],  # Last 10 entries
        "edge_insights": edge_data,
        "predictive_maintenance": maintenance_data,
        "health_score": maintenance_data.get("health_score", 1.0),
        "anomaly_count": len([alert for alert in alerts if alert.get('device_id') == device_id and 'ANOMALY' in alert.get('type', '')])
    }
    
    return jsonify(device_data)

@app.route("/api/devices/<device_id>", methods=["POST"])
def register_device(device_id):
    """Register a new device"""
    data = request.get_json() or {}
    
    device_info = {
        "device_type": data.get("device_type", "unknown"),
        "protocol": data.get("protocol", "unknown"),
        "firmware_version": data.get("firmware_version", "1.0.0"),
        "capabilities": data.get("capabilities", []),
        "registered_at": datetime.utcnow().isoformat() + "Z",
        "status": "active"
    }
    
    device_registry[device_id] = device_info
    
    # Set default configuration
    default_config = {
        "telemetry_interval": data.get("telemetry_interval", 30),
        "heartbeat_interval": data.get("heartbeat_interval", 60),
        "alert_thresholds": {
            "battery": 20,
            "temperature": 40,
            "signal_strength": -100
        }
    }
    device_configs[device_id] = default_config
    
    # Register with industrial protocols if applicable
    protocol = data.get("protocol", "unknown")
    if industrial_manager and protocol == IndustrialProtocol.LORAWAN.value:
        # Extract DevEUI for LoRaWAN devices
        dev_eui = device_id.replace('lorawan_', '')
        industrial_manager.protocols['lorawan'].register_device(dev_eui, device_info)
    
    print(f"[Device Management] Registered device: {device_id}")
    return jsonify({
        "status": "success", 
        "device_id": device_id,
        "config": default_config
    })

@app.route("/api/devices/<device_id>/config", methods=["GET", "PUT"])
def device_config(device_id):
    """Get or update device configuration"""
    if device_id not in device_registry:
        return jsonify({"error": "Device not found"}), 404
    
    if request.method == "GET":
        return jsonify(device_configs.get(device_id, {}))
    
    elif request.method == "PUT":
        new_config = request.get_json()
        if not new_config:
            return jsonify({"error": "No configuration provided"}), 400
        
        # Update configuration
        device_configs[device_id].update(new_config)
        
        # Queue configuration update command
        if device_id not in device_commands:
            device_commands[device_id] = []
        
        device_commands[device_id].append({
            "command_id": str(uuid.uuid4()),
            "type": "config_update",
            "config": new_config,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "pending"
        })
        
        # Send via industrial protocol if applicable
        protocol = device_registry[device_id].get("protocol")
        if industrial_manager and protocol in [p.value for p in IndustrialProtocol]:
            industrial_manager.send_command(device_id, {
                "type": "config_update",
                "parameters": new_config
            }, protocol)
        
        print(f"[Device Management] Updated config for {device_id}")
        return jsonify({"status": "success", "config": device_configs[device_id]})

@app.route("/api/devices/<device_id>/commands", methods=["GET", "POST"])
def device_commands_endpoint(device_id):
    """Get pending commands or send new command to device"""
    if device_id not in device_registry:
        return jsonify({"error": "Device not found"}), 404
    
    if request.method == "GET":
        return jsonify(device_commands.get(device_id, []))
    
    elif request.method == "POST":
        data = request.get_json()
        if not data or "command" not in data:
            return jsonify({"error": "No command provided"}), 400
        
        if device_id not in device_commands:
            device_commands[device_id] = []
        
        command = {
            "command_id": str(uuid.uuid4()),
            "type": data["command"],
            "parameters": data.get("parameters", {}),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "pending"
        }
        
        device_commands[device_id].append(command)
        
        # Send command via appropriate protocol
        protocol = device_registry[device_id].get("protocol")
        
        if protocol == "mqtt":
            try:
                protocol_router.mqtt_handler.client.publish(
                    f"fleet/{device_id}/commands",
                    json.dumps(command)
                )
                command["status"] = "sent"
                print(f"[Device Management] Sent MQTT command to {device_id}: {data['command']}")
            except Exception as e:
                print(f"[Device Management] Failed to send MQTT command to {device_id}: {e}")
        
        elif industrial_manager and protocol in [p.value for p in IndustrialProtocol]:
            # Send via industrial protocol
            success = industrial_manager.send_command(device_id, command, protocol)
            if success:
                command["status"] = "sent"
                print(f"[Device Management] Sent {protocol} command to {device_id}: {data['command']}")
            else:
                print(f"[Device Management] Failed to send {protocol} command to {device_id}")
        
        return jsonify({"status": "success", "command": command})

@app.route("/api/devices/<device_id>/commands/<command_id>/ack", methods=["POST"])
def ack_command(device_id, command_id):
    """Acknowledge command execution from device"""
    if device_id not in device_commands:
        return jsonify({"error": "Device not found"}), 404
    
    for command in device_commands[device_id]:
        if command["command_id"] == command_id:
            command["status"] = "acknowledged"
            command["ack_timestamp"] = datetime.utcnow().isoformat() + "Z"
            print(f"[Device Management] Command {command_id} acknowledged by {device_id}")
            return jsonify({"status": "success"})
    
    return jsonify({"error": "Command not found"}), 404

# ============================================================================
# GEOFENCE MANAGEMENT ROUTES
# ============================================================================

@app.route("/api/geofences", methods=["GET"])
def get_all_geofences():
    """Get all geofences"""
    return jsonify(geofences)

@app.route("/api/devices/<device_id>/geofence", methods=["GET", "POST", "DELETE"])
def device_geofence(device_id):
    """Manage device geofence"""
    if device_id not in device_registry:
        return jsonify({"error": "Device not found"}), 404
    
    if request.method == "GET":
        return jsonify(geofences.get(device_id, {}))
    
    elif request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "No geofence data provided"}), 400
        
        # Validate geofence data
        required_fields = ["center_lat", "center_lon", "radius_km"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields: center_lat, center_lon, radius_km"}), 400
        
        geofence_config = {
            "center_lat": float(data["center_lat"]),
            "center_lon": float(data["center_lon"]),
            "radius_km": float(data["radius_km"]),
            "alert_on_breach": data.get("alert_on_breach", True),
            "alert_on_return": data.get("alert_on_return", False),
            "name": data.get("name", f"Geofence for {device_id}"),
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        geofences[device_id] = geofence_config
        device_geofence_state[device_id] = "inside"  # Assume inside initially
        
        print(f"[Geofence] Created geofence for {device_id}: {geofence_config}")
        return jsonify({"status": "success", "geofence": geofence_config})
    
    elif request.method == "DELETE":
        if device_id in geofences:
            del geofences[device_id]
            if device_id in device_geofence_state:
                del device_geofence_state[device_id]
            print(f"[Geofence] Removed geofence for {device_id}")
            return jsonify({"status": "success"})
        else:
            return jsonify({"error": "No geofence found for device"}), 404

# ============================================================================
# EXISTING ROUTES
# ============================================================================

@app.route("/http/telemetry", methods=["POST"])
def http_telemetry():
    """Handle HTTP telemetry messages"""
    try:
        data = request.get_json()
        if protocol_router:
            protocol_router.handle_http_telemetry(data)
            return jsonify({"status": "success", "message": "Telemetry received"})
        else:
            return jsonify({"status": "error", "message": "Protocol router not ready"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/http/alerts", methods=["POST"])
def http_alerts():
    """Handle HTTP alert messages"""
    try:
        data = request.get_json()
        if protocol_router:
            protocol_router.handle_http_alert(data)
            return jsonify({"status": "success", "message": "Alert received"})
        else:
            return jsonify({"status": "error", "message": "Protocol router not ready"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/coap/telemetry", methods=["POST"])
def coap_telemetry():
    """Handle CoAP telemetry messages via HTTP bridge"""
    try:
        data = request.get_json()
        data["protocol"] = Protocol.COAP.value
        data["received_at"] = datetime.utcnow().isoformat() + "Z"
        enhanced_handle_telemetry(data)
        return jsonify({"status": "success", "message": "CoAP telemetry received"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok", 
        "assets_count": len(assets),
        "devices_count": len(device_registry),
        "geofences_count": len(geofences),
        "edge_devices": len(edge_insights),
        "maintenance_predictions": len(maintenance_predictions),
        "protocols": ["mqtt", "http", "coap", "opcua", "modbus", "lorawan"]
    })

@app.route("/api/assets", methods=["GET"])
def get_assets():
    return jsonify(list(assets.values()))

@app.route("/api/latest", methods=["GET"])
def get_latest():
    return jsonify(list(assets.values()))

@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    return jsonify(list(alerts))

@app.route("/api/protocols", methods=["GET"])
def get_protocols():
    """Show supported protocols"""
    protocol_counts = {}
    for asset in assets.values():
        protocol = asset.get("protocol", "unknown")
        protocol_counts[protocol] = protocol_counts.get(protocol, 0) + 1
        
    return jsonify({
        "supported_protocols": ["mqtt", "http", "coap", "opcua", "modbus", "lorawan"],
        "device_counts": protocol_counts,
        "endpoints": {
            "mqtt": "publish to: fleet/<device_id>/telemetry",
            "http": "POST to: /http/telemetry",
            "coap": "POST to: /coap/telemetry (HTTP bridge) or native CoAP",
            "opcua": "Connect to: opc.tcp://localhost:4840",
            "modbus": "Connect to: localhost:5020",
            "lorawan": "Register devices via /api/protocols/lorawan/devices"
        }
    })

if __name__ == "__main__":
    print(f"[backend] Starting multi-protocol backend on port: {BACKEND_PORT}")
    print("[backend] Supported protocols: MQTT, HTTP, CoAP, OPC-UA, Modbus, LoRaWAN")
    print("[backend] Device management: Enabled")
    print("[backend] Geofencing: Enabled")
    print("[backend] Edge Computing: Enabled")
    print("[backend] Industrial Protocols: Enabled")
    from waitress import serve
    serve(app, host="0.0.0.0", port=BACKEND_PORT)