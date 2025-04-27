import math
import random
from datetime import datetime

class PlantModel:
    """Model for simulating flax plant growth based on environmental conditions"""
    
    def __init__(self, config):
        """Initialize the plant growth model"""
        self.config = config
        self.day = 1
        self.phase = "germination"
        
        # Plant metrics
        self.height = 0.0          # cm
        self.root_length = 0.0     # cm
        self.flowers = 0           # count
        self.appearance = 3.0      # 0-10 scale
        
        # Growth history
        self.history = []
        
        # Current environment
        self.environment = {}
        
        # Internal tracking
        self.stress_level = 0.0
        
        # Recommendations
        self.recommendations = {}
    
    def update(self, day, environment):
        """Update the model with current day and environment"""
        self.day = day
        self.environment = environment.copy()
        
        # Get current phase based on day
        self.phase = self._get_phase_for_day(day)
        
        # Calculate growth based on environment and phase
        self._calculate_growth()
        
        # Generate recommendations for optimal conditions
        self._generate_recommendations()
        
        # Add current state to history
        self.history.append({
            "day": day,
            "phase": self.phase,
            "height": self.height,
            "root_length": self.root_length,
            "flowers": self.flowers,
            "appearance": self.appearance,
            "environment": environment.copy(),
            "timestamp": datetime.now().isoformat()
        })
    
    def get_current_metrics(self):
        """Get current plant growth metrics"""
        return {
            "day": self.day,
            "phase": self.phase,
            "height": round(self.height, 1),
            "root_length": round(self.root_length, 1),
            "flowers": self.flowers,
            "appearance": round(self.appearance, 1),
            "status": self._get_status_description()
        }
    
    def get_current_phase(self):
        """Get the current growth phase"""
        return self.phase
    
    def get_predictions(self):
        """Get predictions for future growth"""
        # Simple prediction using growth rates from config
        remaining_days = {
            "germination": max(0, self.config["PHASES"]["germination"][1] - self.day),
            "growth": max(0, self.config["PHASES"]["growth"][1] - max(self.day, self.config["PHASES"]["growth"][0])),
            "flowering": max(0, self.config["PHASES"]["flowering"][1] - max(self.day, self.config["PHASES"]["flowering"][0])),
            "ripening": max(0, self.config["PHASES"]["ripening"][1] - max(self.day, self.config["PHASES"]["ripening"][0]))
        }
        
        # Predict height at maturity
        predicted_height = self.height
        predicted_root = self.root_length
        predicted_flowers = self.flowers
        
        # Add predicted growth for each remaining phase
        for phase, days in remaining_days.items():
            if days > 0:
                # Simplified prediction - actual growth would depend on future environment
                predicted_height += days * self.config["GROWTH_RATES"][phase]["height"]
                predicted_root += days * self.config["GROWTH_RATES"][phase]["root"]
                predicted_flowers += days * self.config["GROWTH_RATES"][phase]["flowers"]
        
        # Limit to maximum values
        predicted_height = min(predicted_height, self.config["MAX_VALUES"]["height"])
        predicted_root = min(predicted_root, self.config["MAX_VALUES"]["root_length"])
        predicted_flowers = min(predicted_flowers, self.config["MAX_VALUES"]["flowers"])
        
        return {
            "days_to_maturity": sum(remaining_days.values()),
            "predicted_height": round(predicted_height, 1),
            "predicted_root_length": round(predicted_root, 1),
            "predicted_flowers": round(predicted_flowers, 0)
        }
    
    def get_recommendations(self):
        """Get recommendations for optimal growth conditions"""
        return self.recommendations.copy()
    
    def get_history(self):
        """Get growth history"""
        return self.history.copy()
    
    def _get_phase_for_day(self, day):
        """Determine the current growth phase based on the day"""
        phases = self.config["PHASES"]
        
        if phases["germination"][0] <= day <= phases["germination"][1]:
            return "germination"
        elif phases["growth"][0] <= day <= phases["growth"][1]:
            return "growth"
        elif phases["flowering"][0] <= day <= phases["flowering"][1]:
            return "flowering"
        elif phases["ripening"][0] <= day <= phases["ripening"][1]:
            return "ripening"
        else:
            # Default to ripening if beyond all phases
            return "ripening"
    
    def _calculate_growth(self):
        """Calculate growth based on current environment and phase"""
        # Get optimal ranges for current phase
        phase_params = self.config["ENVIRONMENT"][self.phase]
        
        # Calculate growth factor based on how optimal the environment is
        growth_factor = self._calculate_growth_factor()
        
        # Calculate daily growth rates for current phase
        base_height_growth = self.config["GROWTH_RATES"][self.phase]["height"]
        base_root_growth = self.config["GROWTH_RATES"][self.phase]["root"]
        base_flower_growth = self.config["GROWTH_RATES"][self.phase]["flowers"]
        
        # Apply growth factor
        height_growth = base_height_growth * growth_factor
        root_growth = base_root_growth * growth_factor
        flower_growth = base_flower_growth * growth_factor
        
        # Add random variation for natural growth pattern
        variation = random.uniform(0.9, 1.1)
        
        # Update plant metrics
        self.height += height_growth * variation
        self.root_length += root_growth * variation
        self.flowers += flower_growth * variation
        
        # Apply maximum limits
        self.height = min(self.height, self.config["MAX_VALUES"]["height"])
        self.root_length = min(self.root_length, self.config["MAX_VALUES"]["root_length"])
        self.flowers = min(round(self.flowers), self.config["MAX_VALUES"]["flowers"])
        
        # Update appearance based on environment and stress
        self._update_appearance()
    
    def _calculate_growth_factor(self):
        """Calculate growth factor based on environmental conditions"""
        # Start with base growth factor
        growth_factor = 1.0
        self.stress_level = 0.0
        
        # Get optimal ranges for current phase
        phase_params = self.config["ENVIRONMENT"][self.phase]
        
        # Check temperature
        temp = self.environment.get("temperature", 20)
        temp_min, temp_max = phase_params["temperature"][0], phase_params["temperature"][1]
        temp_optimal = (temp_min + temp_max) / 2
        
        if temp < temp_min:
            # Too cold
            temp_penalty = (temp_min - temp) / temp_min
            growth_factor -= temp_penalty * 0.5
            self.stress_level += temp_penalty * 0.3
        elif temp > temp_max:
            # Too hot
            temp_penalty = (temp - temp_max) / temp_max
            growth_factor -= temp_penalty * 0.6
            self.stress_level += temp_penalty * 0.4
        else:
            # Within range - check how close to optimal
            if temp_max == temp_min:
                temp_optimality = 1.0 if temp == temp_optimal else 0.8
            else:
                temp_optimality = 1 - abs(temp - temp_optimal) / (temp_max - temp_min)
            growth_factor += temp_optimality * 0.2
        
        # Ensure growth factor stays within reasonable bounds
        growth_factor = max(0.1, min(growth_factor, 1.2))
        self.stress_level = min(self.stress_level, 1.0)
        
        return growth_factor
    
    def _update_appearance(self):
        """Update the plant's appearance rating based on conditions"""
        # Base appearance range for the current phase
        appearance_range = self.config["APPEARANCE_RATINGS"][self.phase]
        min_appearance, max_appearance = appearance_range
        
        # Calculate appearance modifier based on stress level
        appearance_mod = 1.0 - self.stress_level
        
        # Calculate base appearance for the phase
        base_appearance = min_appearance + (max_appearance - min_appearance) * appearance_mod
        
        # Add small random variation
        variation = random.uniform(-0.3, 0.3)
        
        # Update appearance
        self.appearance = max(0, min(10, base_appearance + variation))
    
    def _get_status_description(self):
        """Return a text description of the plant's current status"""
        if self.appearance >= 8:
            return "Thriving - Vibrant and healthy"
        elif self.appearance >= 6:
            return "Healthy - Growing well"
        elif self.appearance >= 4:
            return "Average - Some minor issues"
        elif self.appearance >= 2:
            return "Struggling - Visible stress signs"
        else:
            return "Critical - Severe stress"
    
    def _generate_recommendations(self):
        """Generate recommendations for optimal growth conditions"""
        # Get optimal ranges for current phase
        phase_params = self.config["ENVIRONMENT"][self.phase]
        
        # For each parameter, recommend the optimal value
        self.recommendations = {
            "temperature": (phase_params["temperature"][0] + phase_params["temperature"][1]) / 2,
            "irrigation": (phase_params["irrigation"][0] + phase_params["irrigation"][1]) / 2,
            "ventilation": (phase_params["ventilation"][0] + phase_params["ventilation"][1]) / 2,
            "light_hours": (phase_params["light_hours"][0] + phase_params["light_hours"][1]) / 2
        }
