# Environmental controller for flax greenhouse
import random
from config import ENVIRONMENT_PARAMS, ERROR_SIMULATION, get_current_phase, get_random_parameter

class EnvironmentController:
    """Controls environmental parameters for the greenhouse simulation"""
    
    def __init__(self, error_simulation=True):
        """Initialize the environment controller"""
        self.current_params = {
            "temperature": 0,
            "ventilation": 0,
            "irrigation": 0,
            "light_hours": 0,
            "temperature_range": (0, 0, 0),
            "ventilation_range": (0, 0, 0),
            "irrigation_range": (0, 0, 0),
            "light_hours_range": (0, 0, 0)
        }
        self.error_simulation = error_simulation
        self.error_active = False
        self.error_description = ""
    
    def set_parameters_for_day(self, day):
        """
        Set environmental parameters based on the current growth phase
        
        Args:
            day: Current simulation day
            
        Returns:
            Dictionary with the environmental parameters for the day
        """
        phase = get_current_phase(day)
        
        # Get parameter ranges for the current phase
        temp_range = ENVIRONMENT_PARAMS[phase]["temperature"]
        vent_range = ENVIRONMENT_PARAMS[phase]["ventilation"]
        irr_range = ENVIRONMENT_PARAMS[phase]["irrigation"]
        light_range = ENVIRONMENT_PARAMS[phase]["light_hours"]
        
        # Store parameter ranges for growth calculation
        self.current_params["temperature_range"] = temp_range
        self.current_params["ventilation_range"] = vent_range
        self.current_params["irrigation_range"] = irr_range
        self.current_params["light_hours_range"] = light_range
        
        # Reset error status
        self.error_active = False
        self.error_description = ""
        
        # Determine if an error/suboptimal condition will occur today
        if self.error_simulation and random.random() < ERROR_SIMULATION["probability"]:
            return self._generate_error_condition(phase)
        
        # Generate random values within the optimal ranges
        self.current_params["temperature"] = get_random_parameter((temp_range[0], temp_range[1]))
        self.current_params["ventilation"] = get_random_parameter((vent_range[0], vent_range[1]))
        self.current_params["irrigation"] = get_random_parameter((irr_range[0], irr_range[1]))
        self.current_params["light_hours"] = get_random_parameter((light_range[0], light_range[1]))
        
        return self.current_params.copy()
    
    def _generate_error_condition(self, phase):
        """
        Generate a suboptimal environmental condition for error simulation
        
        Returns:
            Dictionary with the environmental parameters including an error
        """
        self.error_active = True
        error_param = random.choice(["temperature", "ventilation", "irrigation", "light_hours"])
        
        # Set normal parameters for non-error conditions
        temp_range = ENVIRONMENT_PARAMS[phase]["temperature"]
        vent_range = ENVIRONMENT_PARAMS[phase]["ventilation"]
        irr_range = ENVIRONMENT_PARAMS[phase]["irrigation"]
        light_range = ENVIRONMENT_PARAMS[phase]["light_hours"]
        
        self.current_params["temperature"] = get_random_parameter((temp_range[0], temp_range[1]))
        self.current_params["ventilation"] = get_random_parameter((vent_range[0], vent_range[1]))
        self.current_params["irrigation"] = get_random_parameter((irr_range[0], irr_range[1]))
        self.current_params["light_hours"] = get_random_parameter((light_range[0], light_range[1]))
        
        # Apply error to selected parameter
        if error_param == "temperature":
            # Determine if too hot or too cold
            if random.random() < 0.5:
                # Too cold
                self.current_params["temperature"] = temp_range[0] - random.uniform(1, ERROR_SIMULATION["severity"]["temperature"])
                self.error_description = f"Temperature too low: {self.current_params['temperature']:.1f}°C"
            else:
                # Too hot
                self.current_params["temperature"] = temp_range[1] + random.uniform(1, ERROR_SIMULATION["severity"]["temperature"])
                self.error_description = f"Temperature too high: {self.current_params['temperature']:.1f}°C"
                
        elif error_param == "ventilation":
            # Determine if too little or too much ventilation
            if random.random() < 0.5:
                # Too little
                self.current_params["ventilation"] = max(0.1, vent_range[0] - random.uniform(0.1, ERROR_SIMULATION["severity"]["ventilation"]))
                self.error_description = f"Ventilation too low: {self.current_params['ventilation']:.1f}/hr"
            else:
                # Too much
                self.current_params["ventilation"] = vent_range[1] + random.uniform(0.1, ERROR_SIMULATION["severity"]["ventilation"])
                self.error_description = f"Ventilation too high: {self.current_params['ventilation']:.1f}/hr"
                
        elif error_param == "irrigation":
            # Determine if too little or too much water
            if random.random() < 0.5:
                # Too dry
                self.current_params["irrigation"] = max(10, irr_range[0] - random.uniform(10, ERROR_SIMULATION["severity"]["irrigation"]))
                self.error_description = f"Irrigation too low: {self.current_params['irrigation']:.1f}ml"
            else:
                # Too wet
                self.current_params["irrigation"] = irr_range[1] + random.uniform(10, ERROR_SIMULATION["severity"]["irrigation"])
                self.error_description = f"Irrigation too high: {self.current_params['irrigation']:.1f}ml"
                
        elif error_param == "light_hours":
            # Determine if too little or too much light
            if random.random() < 0.5:
                # Too little
                self.current_params["light_hours"] = max(6, light_range[0] - random.uniform(1, ERROR_SIMULATION["severity"]["light_hours"]))
                self.error_description = f"Light hours too low: {self.current_params['light_hours']:.1f}hrs"
            else:
                # Too much
                self.current_params["light_hours"] = min(24, light_range[1] + random.uniform(1, ERROR_SIMULATION["severity"]["light_hours"]))
                self.error_description = f"Light hours too high: {self.current_params['light_hours']:.1f}hrs"
        
        return self.current_params.copy()
    
    def get_current_parameters(self):
        """Return the current environmental parameters"""
        return self.current_params.copy()
    
    def get_error_status(self):
        """Return error status and description"""
        return {
            "error_active": self.error_active,
            "error_description": self.error_description
        }
    
    def manual_override(self, **kwargs):
        """
        Manually override specific environmental parameters
        
        Args:
            **kwargs: Parameter names and values to override
        """
        for param, value in kwargs.items():
            if param in self.current_params:
                self.current_params[param] = value
        
        return self.current_params.copy()
