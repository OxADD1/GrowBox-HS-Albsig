import time
import threading
from datetime import datetime

class MainController:
    """Central controller that coordinates model, sensors, and hardware"""
    
    def __init__(self, model, mqtt_controller, sensor_manager, hardware_controller, 
                 model_update_interval=60):  # Update model every 60 seconds
        """Initialize the main controller"""
        self.model = model
        self.mqtt = mqtt_controller
        self.sensors = sensor_manager
        self.hardware = hardware_controller
        self.model_update_interval = model_update_interval
        self.running = False
        self.current_day = 0
        self.start_time = None
        
        # Set up MQTT subscriptions
        self._setup_mqtt()
        
        # Register for sensor data
        self.sensors.register_data_callback(self._on_sensor_data)
    
    def _setup_mqtt(self):
        """Set up MQTT topic subscriptions"""
        self.mqtt.subscribe("command/start", self._on_start_command)
        self.mqtt.subscribe("command/stop", self._on_stop_command)
        self.mqtt.subscribe("command/set_hardware", self._on_set_hardware_command)
        self.mqtt.subscribe("command/get_status", self._on_get_status_command)
    
    def start(self):
        """Start the greenhouse control system"""
        # Initialize hardware
        if not self.hardware.initialize():
            print("Failed to initialize hardware")
            return False
        
        # Connect to sensors
        if not self.sensors.connect_sensors():
            print("Failed to connect to sensors")
            return False
        
        # Start MQTT client
        if not self.mqtt.start():
            print("Failed to start MQTT client")
            return False
        
        # Start sensor readings
        self.sensors.start_reading()
        
        # Start the main control loop
        self.running = True
        self.start_time = datetime.now()
        self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
        self.control_thread.start()
        
        print("Greenhouse control system started")
        return True
    
    def stop(self):
        """Stop the greenhouse control system"""
        self.running = False
        
        # Shutdown hardware
        self.hardware.shutdown()
        
        # Stop sensor readings
        self.sensors.stop_reading()
        
        # Disconnect from MQTT
        self.mqtt.stop()
        
        if hasattr(self, 'control_thread'):
            self.control_thread.join(timeout=1.0)
        
        print("Greenhouse control system stopped")
    
    def _control_loop(self):
        """Main control loop"""
        last_model_update = 0
        
        while self.running:
            # Process hardware commands
            self.hardware.process_commands()
            
            # Check if it's time to update the model
            current_time = time.time()
            if current_time - last_model_update >= self.model_update_interval:
                self._update_model()
                last_model_update = current_time
            
            # Adjust hardware based on model recommendations
            self._adjust_hardware_from_model()
            
            # Publish status update
            self._publish_status()
            
            # Sleep to avoid too frequent updates
            time.sleep(1)
    
    def _update_model(self):
        """Update the plant growth model based on sensor data"""
        # Get latest sensor data
        sensor_data = self.sensors.get_latest_data()
        
        # Calculate days since start
        days_running = (datetime.now() - self.start_time).total_seconds() / (24 * 3600)
        self.current_day = int(days_running) + 1  # Start from day 1
        
        # Don't go beyond 80 days in the model
        if self.current_day > 80:
            self.current_day = 80
        
        # Convert sensor data to model parameters
        environment = {
            "temperature": sensor_data.get("air_temperature", 20),
            "irrigation": 0,  # Will be calculated from water pump activity
            "ventilation": 0,  # Will be calculated from fan speed
            "light_hours": 0,  # Will be calculated from light status
            
            # Additional parameters from sensors
            "soil_temperature": sensor_data.get("soil_temperature", 20),
            "soil_moisture": sensor_data.get("soil_moisture", 70)
        }
        
        # Calculate derived parameters from hardware state
        water_pump = self.hardware.get_component_state("water_pump")
        if water_pump["state"]:
            # Convert pump flow rate to daily irrigation amount
            environment["irrigation"] = water_pump["value"] * 1440 / 100  # ml per day
        
        ventilation = self.hardware.get_component_state("ventilation")
        if ventilation["state"]:
            # Convert fan speed to air exchanges per hour
            environment["ventilation"] = 1 + (ventilation["value"] / 100) * 3  # 1-4 exchanges/hour
        
        lights = self.hardware.get_component_state("led_lights")
        if lights["state"]:
            # Assuming we track light on time
            environment["light_hours"] = 14  # Default to 14 hours if on
        
        # Update the model with current environment and day
        self.model.update(self.current_day, environment)
    
    def _adjust_hardware_from_model(self):
        """Adjust hardware settings based on model recommendations"""
        # Get recommendations from the model
        recommendations = self.model.get_recommendations()
        
        # Set heating mat based on temperature needs
        target_temp = recommendations.get("temperature", 20)
        current_temp = self.sensors.get_latest_data().get("air_temperature", 20)
        
        if current_temp < target_temp - 1:
            # Turn on heating if too cold
            self.hardware.set_component_state("heating_mat", True, 100)
        elif current_temp > target_temp + 1:
            # Turn off heating if too hot
            self.hardware.set_component_state("heating_mat", False, 0)
        
        # Set water pump based on irrigation needs
        target_irrigation = recommendations.get("irrigation", 150)  # ml per day
        soil_moisture = self.sensors.get_latest_data().get("soil_moisture", 70)
        
        if soil_moisture < 60:  # If soil is too dry
            # Convert daily irrigation to pump flow rate
            pump_value = min(100, (target_irrigation / 1440) * 100)  # Convert to 0-100%
            self.hardware.set_component_state("water_pump", True, pump_value)
        else:
            # Soil moisture is sufficient
            self.hardware.set_component_state("water_pump", False, 0)
        
        # Set ventilation based on air exchange needs
        target_ventilation = recommendations.get("ventilation", 2)  # exchanges per hour
        
        # Scale from 1-4 exchanges/hour to 0-100% fan speed
        fan_speed = ((target_ventilation - 1) / 3) * 100
        self.hardware.set_component_state("ventilation", True, fan_speed)
        
        # Set lights based on light hour needs
        target_light_hours = recommendations.get("light_hours", 14)
        current_hour = datetime.now().hour
        
        # Simple logic: lights on from 6am to 6am+target_light_hours
        if 6 <= current_hour < (6 + target_light_hours):
            self.hardware.set_component_state("led_lights", True, 100)
        else:
            self.hardware.set_component_state("led_lights", False, 0)
    
    def _publish_status(self):
        """Publish system status to MQTT"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "day": self.current_day,
            "growth_phase": self.model.get_current_phase(),
            "sensor_data": self.sensors.get_latest_data(),
            "hardware_state": {k: self.hardware.get_component_state(k) for k in self.hardware.components},
            "model": {
                "predictions": self.model.get_predictions(),
                "recommendations": self.model.get_recommendations()
            }
        }
        
        self.mqtt.publish("status", status)
    
    # MQTT command handlers
    
    def _on_start_command(self, payload):
        """Handle start command from MQTT"""
        if not self.running:
            self.start()
            self.mqtt.publish("response/start", {"success": True})
    
    def _on_stop_command(self, payload):
        """Handle stop command from MQTT"""
        if self.running:
            self.stop()
            self.mqtt.publish("response/stop", {"success": True})
    
    def _on_set_hardware_command(self, payload):
        """Handle set hardware command from MQTT"""
        try:
            component = payload["component"]
            state = payload["state"]
            value = payload.get("value", 0)
            
            success = self.hardware.set_component_state(component, state, value)
            self.mqtt.publish("response/set_hardware", {"success": success})
        except Exception as e:
            self.mqtt.publish("response/set_hardware", {"success": False, "error": str(e)})
    
    def _on_get_status_command(self, payload):
        """Handle get status command from MQTT"""
        self._publish_status()
    
    # Sensor data callback
    
    def _on_sensor_data(self, sensor_data):
        """Handle new sensor data"""
        # Publish sensor data to MQTT
        self.mqtt.publish("sensor_data", sensor_data)
