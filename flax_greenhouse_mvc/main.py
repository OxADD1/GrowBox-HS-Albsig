import os
import argparse
import signal
import sys
from model.plant_model import PlantModel
from model.config import PHASES, ENVIRONMENT, MAX_VALUES, GROWTH_RATES, APPEARANCE_RATINGS
from model.config import MQTT_CONFIG, SENSOR_CONFIG, HARDWARE_CONFIG
from controller.mqtt_client import MQTTController
from controller.sensor_manager import SensorManager
from controller.hardware_controller import HardwareController
from controller.main_controller import MainController
from view.visualization import Visualizer
from view.report_generator import ReportGenerator

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Flax Greenhouse Control System")
    parser.add_argument("--simulate", action="store_true", help="Run in simulation mode without physical hardware")
    parser.add_argument("--mqtt-broker", type=str, default=MQTT_CONFIG["broker"], help="MQTT broker address")
    parser.add_argument("--mqtt-port", type=int, default=MQTT_CONFIG["port"], help="MQTT broker port")
    parser.add_argument("--interactive", action="store_true", help="Show interactive visualizations")
    parser.add_argument("--no-dashboard", action="store_true", help="Disable dashboard")
    return parser.parse_args()

def signal_handler(sig, frame):
    """Handle interrupt signals"""
    print("\nShutting down gracefully...")
    if 'controller' in globals():
        controller.stop()
    sys.exit(0)

def load_config():
    """Load configuration into a format suitable for the model"""
    config = {
        "PHASES": PHASES,
        "ENVIRONMENT": ENVIRONMENT,
        "MAX_VALUES": MAX_VALUES,
        "GROWTH_RATES": GROWTH_RATES,
        "APPEARANCE_RATINGS": APPEARANCE_RATINGS
    }
    return config

def main():
    """Main entry point for the application"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create required directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/sensor_data", exist_ok=True)
    os.makedirs("data/model_data", exist_ok=True)
    os.makedirs("visuals", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    print("Starting Flax Greenhouse Control System...")
    
    # Initialize components
    config = load_config()
    plant_model = PlantModel(config)
    
    mqtt_controller = MQTTController(
        broker=args.mqtt_broker,
        port=args.mqtt_port,
        client_id=MQTT_CONFIG["client_id"]
    )
    
    sensor_manager = SensorManager(
        data_dir=SENSOR_CONFIG["data_dir"],
        simulation_mode=args.simulate
    )
    
    hardware_controller = HardwareController(
        simulation_mode=args.simulate
    )
    
    # Create the main controller
    global controller
    controller = MainController(
        model=plant_model,
        mqtt_controller=mqtt_controller,
        sensor_manager=sensor_manager,
        hardware_controller=hardware_controller,
        model_update_interval=60  # Update model every minute
    )
    
    # Create visualization and reporting components
    visualizer = Visualizer(save_path="visuals")
    report_generator = ReportGenerator(save_path="reports")
    
    # Register controller with visualizer
    sensor_manager.register_data_callback(lambda data: visualizer.add_data_point({
        "day": controller.current_day,
        "phase": plant_model.get_current_phase(),
        "height": plant_model.height,
        "root_length": plant_model.root_length,
        "flowers": plant_model.flowers,
        "appearance": plant_model.appearance,
        "environment": data,
        "hardware_state": {k: hardware_controller.get_component_state(k) for k in hardware_controller.components}
    }))
    
    # Start the system
    if controller.start():
        print("System started successfully")
        
        # Keep main thread alive
        while True:
            try:
                signal.pause()
            except (KeyboardInterrupt, SystemExit):
                break
            except:
                # signal.pause() is not available on some platforms
                import time
                time.sleep(1)
    else:
        print("Failed to start the system")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
