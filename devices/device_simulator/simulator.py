import os, time, json, random, socket
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = os.getenv("MQTT_BROKER", "broker")
PORT = int(os.getenv("MQTT_PORT", "1883"))

hostname = socket.gethostname()
device_id = os.getenv("DEVICE_ID", f"asset-{hostname}")

lat = float(os.getenv("INIT_LAT", 34.890000))
lon = float(os.getenv("INIT_LON", -1.320000))
battery = float(os.getenv("INIT_BATTERY", random.uniform(60, 100)))
temp = float(os.getenv("INIT_TEMP", random.uniform(24, 32)))

client = mqtt.Client(client_id=device_id)
client.connect(BROKER, PORT, 60)
client.loop_start()

print(f"[simulator] {device_id} -> broker={BROKER}:{PORT}")

def simulate_step():
    global lat, lon, battery, temp
    lat += random.uniform(-0.0008, 0.0008)
    lon += random.uniform(-0.0008, 0.0008)
    battery = max(0, battery - random.uniform(0.05, 0.4))
    temp += random.uniform(-0.15, 0.15)
    status = "OK"
    if battery <= 10:
        status = "CRITICAL_BATTERY"
    elif battery <= 20:
        status = "LOW_BATTERY"
    payload = {
        "device_id": device_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "battery": round(battery, 2),
        "temperature": round(temp, 2),
        "status": status
    }
    topic = f"fleet/{device_id}/telemetry"
    client.publish(topic, json.dumps(payload))
    print(f"[{device_id}] -> {topic} : {payload}")

if __name__ == '__main__':
    interval = float(os.getenv("PUB_INTERVAL", 5))
    try:
        while True:
            simulate_step()
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
