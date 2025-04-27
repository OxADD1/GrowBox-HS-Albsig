class EnvironmentModel:
    """Model for environmental conditions in the greenhouse"""
    
    def __init__(self, config):
        """Initialize the environment model"""
        self.config = config
        self.current_phase = "germination"
        self.current_conditions = {}
        self.history = []
    
    def update(self, phase, sensor_data):
        """Update the environment model with current conditions"""
        self.current_phase = phase
        
        # Process sensor data
        self.current_conditions = {
            "temperature": sensor_data.get("air_temperature", 20),
            "soil_temperature": sensor_data.get("soil_temperature", 18),
            "humidity": sensor_data.get("air_humidity", 60),
            "soil_moisture": sensor_data.get("soil_moisture", 70),
            "light_intensity": sensor_data.get("light_intensity", 1000),
            "timestamp": sensor_data.get("timestamp")
        }
        
        # Add derived metrics
        self._calculate_derived_metrics()
        
        # Add to history
        self.history.append(self.current_conditions.copy())
        
        return self.current_conditions
    
    def get_current_conditions(self):
        """Get the current environmental conditions"""
        return self.current_conditions.copy()
    
    def get_optimal_conditions(self, phase=None):
        """Get the optimal conditions for a specific growth phase"""
        if phase is None:
            phase = self.current_phase
            
        if phase not in self.config["ENVIRONMENT"]:
            return {}
            
        phase_params = self.config["ENVIRONMENT"][phase]
        
        # Return optimal values (middle of ranges)
        return {
            "temperature": (phase_params["temperature"][0] + phase_params["temperature"][1]) / 2,
            "ventilation": (phase_params["ventilation"][0] + phase_params["ventilation"][1]) / 2,
            "irrigation": (phase_params["irrigation"][0] + phase_params["irrigation"][1]) / 2,
            "light_hours": (phase_params["light_hours"][0] + phase_params["light_hours"][1]) / 2
        }
    
    def get_environment_quality(self):
        """Evaluate the quality of current environment (0-1 scale)"""
        if not self.current_conditions or self.current_phase not in self.config["ENVIRONMENT"]:
            return 0.5
            
        phase_params = self.config["ENVIRONMENT"][self.current_phase]
        
        # Calculate how close each parameter is to optimal range
        quality_scores = []
        
        # Temperature quality
        temp = self.current_conditions.get("temperature", 20)
        temp_min, temp_max = phase_params["temperature"]
        if temp < temp_min:
            # Too cold
            quality_scores.append(max(0, 1 - (temp_min - temp) / temp_min))
        elif temp > temp_max:
            # Too hot
            quality_scores.append(max(0, 1 - (temp - temp_max) / temp_max))
        else:
            # In range
            quality_scores.append(1.0)
        
        # Overall quality is average of individual scores
        if quality_scores:
            return sum(quality_scores) / len(quality_scores)
        return 0.5
    
    def _calculate_derived_metrics(self):
        """Calculate derived environmental metrics"""
        # Example: Vapor pressure deficit (VPD)
        if "temperature" in self.current_conditions and "humidity" in self.current_conditions:
            temp = self.current_conditions["temperature"]
            humidity = self.current_conditions["humidity"]
            
            # Simple VPD calculation
            self.current_conditions["vpd"] = (1 - humidity/100) * (0.6 * temp)
