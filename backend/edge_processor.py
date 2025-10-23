# virtual-fleet-tracking/backend/edge_processor.py
import numpy as np
import json
import math
from datetime import datetime, timedelta
import logging

class EdgeIntelligence:
    def __init__(self):
        self.anomaly_models = {}
        self.pattern_cache = {}
        self.compression_enabled = True
        print("🧠 Edge Intelligence Initialized")
        
    def detect_anomalies(self, device_id, telemetry_data):
        """Real-time anomaly detection at the edge"""
        try:
            if device_id not in self.anomaly_models:
                # Initialize model when we have enough data
                if device_id not in self.pattern_cache:
                    self.pattern_cache[device_id] = []
                return False
            
            # Extract features for ML model
            features = self._extract_features(telemetry_data)
            
            if len(self.pattern_cache.get(device_id, [])) > 10:  # Enough data for training
                # Train model on recent data
                from sklearn.ensemble import IsolationForest
                
                if device_id not in self.anomaly_models:
                    self.anomaly_models[device_id] = IsolationForest(contamination=0.1, random_state=42)
                
                model = self.anomaly_models[device_id]
                training_data = np.array(self.pattern_cache[device_id][-50:])  # Last 50 points
                
                model.fit(training_data)
                prediction = model.predict([features])[0]
                is_anomaly = prediction == -1
                
                if is_anomaly:
                    self._trigger_anomaly_alert(device_id, telemetry_data, features)
                
                return is_anomaly
            
            # Cache current data point
            self.pattern_cache[device_id].append(features)
            return False
            
        except Exception as e:
            logging.error(f"Anomaly detection failed for {device_id}: {e}")
            return False
    
    def _extract_features(self, telemetry):
        """Extract ML features from telemetry data"""
        try:
            return np.array([
                float(telemetry.get('battery', 0)),
                float(telemetry.get('temperature', 0)),
                float(telemetry.get('signal_strength', 0)),
                float(telemetry.get('lat', 0)),
                float(telemetry.get('lon', 0))
            ])
        except:
            return np.array([0, 0, 0, 0, 0])
    
    def _trigger_anomaly_alert(self, device_id, telemetry, features):
        """Trigger alerts for detected anomalies"""
        try:
            alert_type = self._classify_anomaly_type(features)
            
            alert_data = {
                "device_id": device_id,
                "type": f"EDGE_ANOMALY_{alert_type}",
                "severity": "high",
                "details": {
                    "detected_at": datetime.utcnow().isoformat() + "Z",
                    "battery": telemetry.get('battery'),
                    "temperature": telemetry.get('temperature'),
                    "location": [telemetry.get('lat'), telemetry.get('lon')],
                    "anomaly_type": alert_type
                },
                "processed_at_edge": True
            }
            
            print(f"🚨 Edge Anomaly Detected: {device_id} - {alert_type}")
            return alert_data
            
        except Exception as e:
            logging.error(f"Anomaly alert trigger failed: {e}")
            return None
    
    def _classify_anomaly_type(self, features):
        """Classify type of anomaly"""
        try:
            battery, temp, signal, lat, lon = features
            
            if battery < 10:
                return "CRITICAL_BATTERY"
            elif temp > 45:
                return "OVERHEATING"
            elif signal < -120:
                return "SIGNAL_DEGRADATION"
            else:
                return "BEHAVIORAL_ANOMALY"
        except:
            return "UNKNOWN_ANOMALY"
    
    def compress_telemetry(self, device_id, current_data, previous_data):
        """Smart data compression - send only significant changes"""
        try:
            if not self.compression_enabled or not previous_data:
                return current_data, True  # Send full data
            
            # Calculate changes
            battery_change = abs(float(current_data.get('battery', 0)) - float(previous_data.get('battery', 0)))
            temp_change = abs(float(current_data.get('temperature', 0)) - float(previous_data.get('temperature', 0)))
            position_change = self._calculate_distance(
                float(current_data.get('lat', 0)), float(current_data.get('lon', 0)),
                float(previous_data.get('lat', 0)), float(previous_data.get('lon', 0))
            )
            
            # Compression thresholds
            thresholds = {
                'battery': 2.0,  # 2% change
                'temperature': 1.0,  # 1°C change
                'position': 0.01,  # ~1km change
            }
            
            # Check if changes are significant
            significant_change = (
                battery_change > thresholds['battery'] or
                temp_change > thresholds['temperature'] or
                position_change > thresholds['position']
            )
            
            if significant_change:
                compressed_data = {
                    'device_id': current_data['device_id'],
                    'timestamp': current_data['timestamp'],
                    'lat': current_data.get('lat'),
                    'lon': current_data.get('lon'),
                    'battery': current_data.get('battery'),
                    'temperature': current_data.get('temperature'),
                    'compressed': True,
                    'changes_since_last': {
                        'battery_delta': battery_change,
                        'temp_delta': temp_change,
                        'position_delta_km': position_change
                    }
                }
                return compressed_data, True
            else:
                return None, False  # Don't send
                
        except Exception as e:
            logging.error(f"Compression failed for {device_id}: {e}")
            return current_data, True  # Fallback: send full data
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points in km"""
        try:
            from math import radians, sin, cos, sqrt, atan2
            R = 6371  # Earth radius in km
            
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            
            return R * c
        except:
            return 0.0

class PredictiveMaintenance:
    def __init__(self):
        self.device_health_scores = {}
        self.maintenance_predictions = {}
        print("🔧 Predictive Maintenance Initialized")
    
    def analyze_health_trends(self, device_id, telemetry_history):
        """Predict maintenance needs based on historical data"""
        try:
            if len(telemetry_history) < 5:
                return None
            
            battery_trend = self._calculate_battery_degradation(telemetry_history)
            usage_patterns = self._analyze_usage_patterns(telemetry_history)
            
            health_score = self._calculate_health_score(battery_trend, usage_patterns)
            self.device_health_scores[device_id] = health_score
            
            # Predict maintenance
            if health_score < 0.3:
                days_until_maintenance = 7
            elif health_score < 0.6:
                days_until_maintenance = 30
            else:
                days_until_maintenance = 90
            
            prediction = {
                "device_id": device_id,
                "health_score": round(health_score, 2),
                "predicted_maintenance_date": (datetime.utcnow() + timedelta(days=days_until_maintenance)).isoformat() + "Z",
                "confidence": 0.85,
                "recommended_actions": self._generate_maintenance_actions(health_score, battery_trend),
                "battery_degradation_rate": round(battery_trend, 4)
            }
            
            self.maintenance_predictions[device_id] = prediction
            return prediction
            
        except Exception as e:
            logging.error(f"Predictive maintenance failed for {device_id}: {e}")
            return None
    
    def _calculate_battery_degradation(self, history):
        """Calculate battery degradation rate"""
        try:
            if len(history) < 3:
                return 0
            
            batteries = [float(point.get('battery', 0)) for point in history[-10:]]
            if len(batteries) < 2:
                return 0
            
            # Simple linear regression for degradation rate
            x = list(range(len(batteries)))
            y = batteries
            
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(xi**2 for xi in x)
            
            try:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
                return slope
            except:
                return 0
        except:
            return 0
    
    def _analyze_usage_patterns(self, history):
        """Analyze device usage patterns"""
        try:
            movements = []
            temperatures = []
            
            for point in history[-20:]:
                try:
                    movements.append((float(point.get('lat', 0)), float(point.get('lon', 0))))
                    temperatures.append(float(point.get('temperature', 0)))
                except:
                    continue
            
            # Calculate movement intensity
            movement_intensity = self._calculate_movement_intensity(movements) if movements else 0
            temp_variation = np.std(temperatures) if temperatures else 0
            
            return {
                "movement_intensity": movement_intensity,
                "temperature_variation": temp_variation
            }
        except:
            return {"movement_intensity": 0, "temperature_variation": 0}
    
    def _calculate_movement_intensity(self, movements):
        """Calculate how much the device moves"""
        try:
            if len(movements) < 2:
                return 0
            
            total_distance = 0
            for i in range(1, len(movements)):
                lat1, lon1 = movements[i-1]
                lat2, lon2 = movements[i]
                distance = self._calculate_distance(lat1, lon1, lat2, lon2)
                total_distance += distance
            
            return total_distance / (len(movements) - 1)
        except:
            return 0
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points in km"""
        try:
            from math import radians, sin, cos, sqrt, atan2
            R = 6371  # Earth radius in km
            
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            
            return R * c
        except:
            return 0
    
    def _calculate_health_score(self, battery_trend, usage_patterns):
        """Calculate overall device health score (0-1)"""
        try:
            # Battery health (40% weight)
            battery_score = max(0, min(1, 1 + battery_trend * 10))  # Convert degradation rate to score
            
            # Usage pattern health (30% weight)
            movement_score = 1 - min(1, usage_patterns["movement_intensity"] / 100)  # Normalize
            temp_score = 1 - min(1, usage_patterns["temperature_variation"] / 20)  # Normalize
            
            usage_score = (movement_score + temp_score) / 2
            
            # Overall health score
            health_score = (battery_score * 0.4) + (usage_score * 0.3) + 0.3  # 30% base score
            
            return max(0, min(1, health_score))
        except:
            return 0.8  # Default health score
    
    def _generate_maintenance_actions(self, health_score, battery_trend):
        """Generate recommended maintenance actions"""
        try:
            actions = []
            
            if health_score < 0.3:
                actions.extend(["Immediate battery check", "Full diagnostic", "Consider replacement"])
            elif health_score < 0.6:
                actions.extend(["Scheduled maintenance", "Battery calibration", "Firmware update"])
            else:
                actions.append("Routine check")
            
            if battery_trend < -0.5:
                actions.append("Battery replacement recommended")
            
            return actions
        except:
            return ["Routine check"]

# Global edge processor instance
edge_processor = EdgeIntelligence()
predictive_maintenance = PredictiveMaintenance()