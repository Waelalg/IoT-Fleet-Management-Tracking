# virtual-fleet-tracking/backend/protocol_router.py
import json
import threading
import logging
from datetime import datetime
from enum import Enum
import paho.mqtt.client as mqtt

class Protocol(Enum):
    MQTT = "mqtt"
    COAP = "coap"
    HTTP = "http"

class ProtocolRouter:
    def __init__(self, telemetry_callback, alert_callback):
        self.telemetry_callback = telemetry_callback
        self.alert_callback = alert_callback
        self.logger = logging.getLogger(__name__)
        
        # Initialize protocol handlers
        self.mqtt_handler = MQTTHandler(telemetry_callback, alert_callback)
        
    def start_all(self):
        """Start all protocol servers"""
        self.logger.info("Starting protocol servers...")
        
        # Start MQTT
        self.mqtt_handler.connect_and_subscribe()
        
        self.logger.info("Protocol servers started")
        
    def handle_http_telemetry(self, data):
        """Handle HTTP telemetry via Flask"""
        data["protocol"] = Protocol.HTTP.value
        data["received_at"] = datetime.utcnow().isoformat() + "Z"
        self.telemetry_callback(data)
        
    def handle_http_alert(self, data):
        """Handle HTTP alerts via Flask"""
        data["protocol"] = Protocol.HTTP.value
        data["received_at"] = datetime.utcnow().isoformat() + "Z"
        self.alert_callback(data)

class MQTTHandler:
    def __init__(self, telemetry_callback, alert_callback):
        self.telemetry_callback = telemetry_callback
        self.alert_callback = alert_callback
        self.client = mqtt.Client()
        self.broker = "broker"
        self.port = 1883
        
    def connect_and_subscribe(self):
        """Connect to MQTT broker and subscribe to topics"""
        try:
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            print(f"[MQTT] Connected to {self.broker}:{self.port}")
            return True
        except Exception as e:
            print(f"[MQTT] Connection failed: {e}")
            return False
            
    def _on_connect(self, client, userdata, flags, rc):
        print(f"[MQTT] Connected with result code {rc}")
        client.subscribe("fleet/+/telemetry")
        client.subscribe("fleet/+/alerts")
        client.subscribe("fleet/+/commands")
        
    def _on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode("utf-8")
            data = json.loads(payload)
            data["protocol"] = Protocol.MQTT.value
            data["received_at"] = datetime.utcnow().isoformat() + "Z"
            
            if "telemetry" in msg.topic:
                self.telemetry_callback(data)
            elif "alerts" in msg.topic:
                self.alert_callback(data)
                
        except Exception as e:
            print(f"[MQTT] Message processing error: {e}")