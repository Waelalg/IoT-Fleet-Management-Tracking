**Virtual Fleet Tracking System**
A comprehensive IoT fleet tracking solution with multi-protocol support, edge computing capabilities, and industrial protocol integration.

**🚀 Overview**
Virtual Fleet Tracking is a sophisticated IoT platform that enables real-time monitoring and management of connected devices across multiple communication protocols. The system features advanced capabilities including edge computing, predictive maintenance, geofencing, and industrial protocol support.

<img width="1919" height="926" alt="Screenshot 2025-10-23 112750" src="https://github.com/user-attachments/assets/224b1b1b-1bd2-4039-ac19-f780db46d6a5" />


**✨ Key Features**

  **Multi-Protocol Support**
  
    MQTT: Primary protocol for real-time telemetry

    HTTP: RESTful API for device communication

    CoAP: Constrained Application Protocol for low-power devices

    OPC-UA: Industrial automation protocol

    Modbus: Industrial device communication

    LoRaWAN: Long-range, low-power wide-area network

  **Edge Computing & Intelligence**
  
    Real-time anomaly detection using machine learning

    Smart data compression to reduce bandwidth usage

    Local processing for faster response times

    Pattern recognition and behavioral analysis

  **Predictive Maintenance**
  
    Health score calculation for devices

    Battery degradation tracking

    Maintenance prediction algorithms

    Automated alerting for maintenance needs

  **Device Management**
  
    Automatic device registration and configuration

    Remote command execution

    Firmware version tracking

    Capability-based device management

  **Geofencing**
  
    Circular geofence configuration

    Real-time breach detection

    Configurable alerts for entry/exit

    Distance calculation using Haversine formula

  **Industrial Protocol Integration**
    
    OPC-UA simulator for industrial devices
  
    Modbus protocol support

    LoRaWAN device management

    Industrial-grade communication patterns
    
**🏗️ System Architecture**    

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Device        │    │   Backend        │    │   Dashboard     │
│   Simulators    │───▶│   (Flask App)    │───▶│   (React)       │
│                 │    │                  │    │                 │
│ - MQTT Devices  │    │ - Protocol Router│    │ - Real-time     │
│ - HTTP Clients  │    │ - Edge Processor │    │   Monitoring    │
│ - CoAP Devices  │    │ - Industrial     │    │ - Device        │
│ - LoRaWAN       │    │   Protocols      │    │   Management    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              │
                      ┌──────────────────┐
                      │   MQTT Broker    │
                      │   (Mosquitto)    │
                      └──────────────────┘

**📁 Project Structure**

  virtual-fleet-tracking/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── edge_processor.py      # Edge computing intelligence
│   ├── industrial_protocols.py # Industrial protocol handlers
│   ├── protocol_router.py     # Multi-protocol router
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Backend container definition
├── dashboard/
│   ├── src/                  # React application source
│   ├── public/               # Static assets
│   ├── package.json          # Node.js dependencies
│   └── Dockerfile            # Dashboard container definition
├── devices/
│   └── device_simulator/
│       ├── advanced_simulator.py      # Advanced device simulation
│       ├── coap_device.py             # CoAP device simulator
│       ├── geofence_simulator.py      # Geofence testing simulator
│       ├── http_device.py             # HTTP device simulator
│       ├── managed_device.py          # Managed device with commands
│       ├── multi_device_simulator.py  # Multi-device simulator
│       ├── protocol_test_clients.py   # Protocol testing clients
│       ├── simulator.py               # Basic device simulator
│       ├── test_managed_devices.py    # Managed device tests
│       ├── requirements.txt           # Simulator dependencies
│       └── Dockerfile                # Simulator container definition
├── mosquitto/
│   └── config/
│       └── mosquitto.conf     # MQTT broker configuration
├── test_features.py           # Feature testing script
├── test_multi_protocol.py     # Multi-protocol testing
└── docker-compose.yml         # Docker composition



**🛠️ Installation & Setup**

  **Prerequisites**
  
    Docker and Docker Compose

    Python 3.9+ (for local development)

    Node.js 18+ (for dashboard development)

**Quick Start with Docker**

  **Clone the repository**
    git clone <repository-url>
    cd virtual-fleet-tracking
  **Start the system**
    docker-compose up -d
  **Access the services**
  
    Dashboard: http://localhost:3000
    Backend API: http://localhost:5002
    MQTT Broker: localhost:1883

**📡 Protocol Endpoints**

**MQTT**
Telemetry: fleet/{device_id}/telemetry

Alerts: fleet/{device_id}/alerts

Commands: fleet/{device_id}/commands

**HTTP**
Telemetry: POST /http/telemetry

Alerts: POST /http/alerts

CoAP Bridge: POST /coap/telemetry

**REST API Endpoints**
Device Management
GET /api/devices - List all devices

POST /api/devices/{device_id} - Register device

GET /api/devices/{device_id} - Get device details

PUT /api/devices/{device_id}/config - Update device configuration

Commands
GET /api/devices/{device_id}/commands - Get pending commands

POST /api/devices/{device_id}/commands - Send command to device

POST /api/devices/{device_id}/commands/{command_id}/ack - Acknowledge command

Geofencing
GET /api/geofences - List all geofences

POST /api/devices/{device_id}/geofence - Set device geofence

DELETE /api/devices/{device_id}/geofence - Remove geofence

Edge Computing
GET /api/edge/insights - Get edge computing insights

GET /api/devices/{device_id}/edge - Get device edge insights

GET /api/devices/{device_id}/maintenance - Get maintenance predictions

GET /api/analytics/health-scores - Get all device health scores

Industrial Protocols
GET /api/protocols/industrial - Get industrial protocol status

GET /api/protocols/lorawan/devices - List LoRaWAN devices

POST /api/protocols/lorawan/devices - Register LoRaWAN device

POST /api/protocols/lorawan/{dev_eui}/downlink - Send LoRaWAN command


**🚀 Advanced Features**<img width="1919" height="926" alt="Screenshot 2025-10-23 112750" src="https://github.com/user-attachments/assets/61ce9587-35ab-40ca-82f7-90daf86fe4dc" />
<img width="1919" height="926" alt="Screenshot 2025-10-23 112750" src="https://github.com/user-attachments/assets/313169f2-ff75-46cc-aebc-5bcec09055e3" />

**Edge Computing**
The system includes sophisticated edge computing capabilities:

Anomaly Detection: Machine learning-based detection of abnormal device behavior

Data Compression: Smart compression to reduce bandwidth usage

Local Processing: Edge-based processing for faster response times

**Predictive Maintenance**
Health Scoring: Calculates device health based on multiple factors

Battery Analysis: Tracks battery degradation over time

Maintenance Prediction: Predicts when maintenance will be required

Automated Alerts: Sends alerts for critical maintenance needs

**Industrial Protocol Support**
OPC-UA: Industrial automation standard for secure data exchange

Modbus: Serial communication protocol for industrial devices

LoRaWAN: Long-range, low-power protocol for IoT devices
