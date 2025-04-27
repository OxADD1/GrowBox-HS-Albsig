# Flax Greenhouse Control System

This project implements a Model-View-Controller (MVC) architecture for controlling an indoor greenhouse for flax plants with multiple sensors and remote control capabilities.

## Features

- 80-day growing cycle simulation for flax plants
- Real-time sensor data collection every 10 seconds
- MQTT communication for remote control
- Environmental control (temperature, irrigation, ventilation, light)
- Data visualization and reporting
- Soil and air sensors for comprehensive monitoring

## Components

### Model
- Plant growth simulation
- Environmental condition modeling
- Automatic parameter recommendations

### Controller
- MQTT client for remote communication
- Sensor data processing
- Hardware control

### View
- Data visualization
- Report generation

## Usage

```bash
# Run in simulation mode
python main.py --simulate

# Run with interactive visualization
python main.py --simulate --interactive

# Connect to a specific MQTT broker
python main.py --simulate --mqtt-broker 192.168.0.100
