import time
import threading
import random  # For simulation when hardware not connected
import json
import os
from datetime import datetime

class SensorManager:
    """Manages physical sensors and provides sensor data"""
    
    def __init__(self, data_dir="data/sensor_data", simulation_mode=False):
        """Initialize the sensor manager"""
        self.data_dir = data_dir
        self.simulation_mode = simulation_mode
        self.sensors = {
            "soil_temperature": None,  # Temperature sensor in the soil
            "soil_moisture": None,     # Moisture sensor in the soil
            "air_temperature": None,   # Air temperature sensor
            "air_humidity": None,      # Air humidity sensor
            "light_intensity": None    # Light intensity sensor
        }
        self.sensor_data = {k: 0 for k in self.sensors.keys()}
        self.running = False
        self.data_callbacks = []
        self.read_interval = 10  # seconds between sensor readings
        
        # Initialize log file
        self._init_data_logging()
    
    def _init_data_logging(self):
        """Initialize the sensor data log file"""
        os.makedirs(self.data_dir, exist_ok=True)
        self.log_file = f"{self.data_dir}/sensor_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Create CSV header
        with open(self.log_file, 'w') as f:
            header = "timestamp," + ",".join(self.sensors.keys()) + "\n"
            f.write(header)
    
    def connect_sensors(self):
        """Connect to physical sensors or initialize simulation"""
        if not self.simulation_mode:
            try:
                # Here you would initialize your actual sensor hardware
                # Example: self.sensors["soil_temperature"] = SoilTempSensor(pin=4)
                # For now, we'll just simulate success
                print("Connected to physical sensors")
                return True
            except Exception as e:
                print(f"Error connecting to sensors: {e}")
                print("Falling back to simulation mode")
                self.simulation_mode = True
        
        print("Running in sensor simulation mode")
        return True
    
    def start_reading(self):
        """Start reading sensor data at regular intervals"""
        self.running = True
        self.reader_thread = threading.Thread(target=self._sensor_reading_loop, daemon=True)
        self.reader_thread.start()
    
    def stop_reading(self):
        """Stop the sensor reading loop"""
        self.running = False
        if hasattr(self, 'reader_thread'):
            self.reader_thread.join(timeout=1.0)
    
    def get_latest_data(self):
        """Return the most recent sensor readings"""
        return self.sensor_data.copy()
    
    def register_data_callback(self, callback):
        """Register a function to be called with new sensor data"""
        self.data_callbacks.append(callback)
    
    def _sensor_reading_loop(self):
        """Main loop for reading sensors at regular intervals"""
        while self.running:
            # Get sensor readings
            self._read_sensors()
            
            # Log the data
            self._log_sensor_data()
            
            # Call any registered callbacks with the new data
            for callback in self.data_callbacks:
                callback(self.sensor_data)
            
            # Wait for next reading
            time.sleep(self.read_interval)
    
    def _read_sensors(self):
        """Read all sensors and update the sensor_data dict"""
        timestamp = datetime.now().isoformat()
        self.sensor_data["timestamp"] = timestamp
        
        if self.simulation_mode:
            # Simulate sensor readings
            self.sensor_data["soil_temperature"] = round(random.uniform(18, 22), 1)
            self.sensor_data["soil_moisture"] = round(random.uniform(60, 80), 1)
            self.sensor_data["air_temperature"] = round(random.uniform(20, 24), 1)
            self.sensor_data["air_humidity"] = round(random.uniform(50, 70), 1)
            self.sensor_data["light_intensity"] = round(random.uniform(800, 1200), 1)
        else:
            # Read from actual sensors
            # Example: self.sensor_data["soil_temperature"] = self.sensors["soil_temperature"].read()
            pass
    
    def _log_sensor_data(self):
        """Log sensor data to CSV file"""
        with open(self.log_file, 'a') as f:
            values = [self.sensor_data["timestamp"]] + [str(self.sensor_data[k]) for k in self.sensors.keys()]
            f.write(",".join(values) + "\n")
