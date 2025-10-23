import requests
import json
import time

BASE_URL = "http://localhost:5002"

def test_industrial_protocols():
    print("Testing Industrial Protocols...")
    
    # Test industrial status
    response = requests.get(f"{BASE_URL}/api/protocols/industrial")
    if response.status_code == 200:
        data = response.json()
        print("✅ Industrial Protocols:", data)
    else:
        print("❌ Industrial Protocols failed:", response.text)

def test_lorawan():
    print("\nTesting LoRaWAN...")
    
    # Register device
    response = requests.post(
        f"{BASE_URL}/api/protocols/lorawan/devices",
        json={
            "dev_eui": "test-lorawan-001",
            "device_type": "tracker",
            "capabilities": ["gps"]
        }
    )
    if response.status_code == 200:
        print("✅ LoRaWAN device registered")
    else:
        print("❌ LoRaWAN registration failed:", response.text)
    
    # Send command
    response = requests.post(
        f"{BASE_URL}/api/protocols/lorawan/test-lorawan-001/downlink",
        json={"command": "ping"}
    )
    if response.status_code == 200:
        print("✅ LoRaWAN command sent")
    else:
        print("❌ LoRaWAN command failed:", response.text)

def test_edge_features():
    print("\nTesting Edge Features...")
    
    # Send multiple telemetry points to build history
    for i in range(5):
        response = requests.post(
            f"{BASE_URL}/http/telemetry",
            json={
                "device_id": "test-edge-001",
                "protocol": "http", 
                "lat": 34.89 + (i * 0.001),
                "lon": -1.32 + (i * 0.001),
                "battery": 80 - (i * 2),  # Decreasing battery
                "temperature": 25 + i,    # Increasing temperature
                "signal_strength": -90
            }
        )
        if response.status_code == 200:
            print(f"✅ Edge telemetry {i+1} sent")
        else:
            print(f"❌ Edge telemetry {i+1} failed:", response.text)
        time.sleep(1)
    
    # Wait for processing
    time.sleep(2)
    
    # Check edge insights
    response = requests.get(f"{BASE_URL}/api/edge/insights")
    if response.status_code == 200:
        data = response.json()
        print("✅ Edge insights:", len(data), "devices")
        if data:
            for device_id, insights in data.items():
                print(f"   - {device_id}: {insights}")
    else:
        print("❌ Edge insights failed:", response.text)
    
    # Check maintenance data
    response = requests.get(f"{BASE_URL}/api/devices/test-edge-001/maintenance")
    if response.status_code == 200:
        data = response.json()
        print("✅ Maintenance data:", data.get('health_score', 'N/A'))
    else:
        print("❌ Maintenance data failed:", response.text)

def test_anomaly_detection():
    print("\nTesting Anomaly Detection...")
    
    # Send telemetry that should trigger anomaly
    response = requests.post(
        f"{BASE_URL}/http/telemetry",
        json={
            "device_id": "test-anomaly-001",
            "protocol": "http", 
            "lat": 34.89,
            "lon": -1.32,
            "battery": 8,  # Very low battery - should trigger anomaly
            "temperature": 50,  # High temperature - should trigger anomaly
            "signal_strength": -130  # Poor signal
        }
    )
    if response.status_code == 200:
        print("✅ Anomaly telemetry sent")
    else:
        print("❌ Anomaly telemetry failed:", response.text)
    
    # Check alerts
    time.sleep(1)
    response = requests.get(f"{BASE_URL}/api/alerts")
    if response.status_code == 200:
        alerts = response.json()
        edge_alerts = [a for a in alerts if 'EDGE_ANOMALY' in a.get('type', '')]
        print(f"✅ Found {len(edge_alerts)} edge anomaly alerts")
    else:
        print("❌ Alerts check failed:", response.text)

if __name__ == "__main__":
    test_industrial_protocols()
    test_lorawan() 
    test_edge_features()
    test_anomaly_detection()