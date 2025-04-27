# Plant growth simulation for flax plants
import math
import random
from config import PLANT_PARAMS, APPEARANCE_RATINGS, get_current_phase, get_phase_day, get_phase_length

class FlaxPlant:
    """Class representing a flax plant with growth metrics"""
    
    def __init__(self, plant_id=1):
        """Initialize a new flax plant"""
        self.plant_id = plant_id
        self.height = 0.0          # Plant height in cm
        self.root_length = 0.0     # Root length in cm
        self.flowers = 0           # Number of flowers
        self.appearance = 3.0      # Appearance rating (0-10)
        
        # Growth tracking
        self.daily_growth = []     # Track daily growth metrics
        self.stress_level = 0.0    # Plant stress level (0-1)
        
    def update_growth(self, day, environment):
        """
        Update plant growth based on environmental conditions
        
        Args:
            day: Current simulation day
            environment: Dictionary of environmental parameters
        """
        phase = get_current_phase(day)
        phase_day = get_phase_day(day, phase)
        phase_length = get_phase_length(phase)
        
        # Calculate growth factors based on environmental conditions
        growth_factor = self._calculate_growth_factor(environment, phase)
        
        # Calculate non-linear growth based on sigmoid function for more realistic growth patterns
        # Sigmoid function creates an S-shaped curve that's steep in the middle and flattens at the ends
        phase_progress = phase_day / phase_length
        sigmoid_factor = 1 / (1 + math.exp(-10 * (phase_progress - 0.5))) if phase_length > 0 else 0
        
        # Calculate height growth
        max_height_growth = PLANT_PARAMS["max_height"] * PLANT_PARAMS["height_growth_factors"][phase] / phase_length
        height_growth = max_height_growth * sigmoid_factor * growth_factor
        
        # Calculate root growth
        max_root_growth = PLANT_PARAMS["max_root_length"] * PLANT_PARAMS["root_growth_factors"][phase] / phase_length
        root_growth = max_root_growth * sigmoid_factor * growth_factor
        
        # Calculate flower growth (only in flowering and ripening phases)
        max_flower_growth = 0
        if phase in ["flowering", "ripening"]:
            max_flower_growth = PLANT_PARAMS["max_flowers"] * PLANT_PARAMS["flower_growth_factors"][phase] / phase_length
        flower_growth = max_flower_growth * sigmoid_factor * growth_factor
        
        # Apply random variation (±10%) for more natural growth
        variation = random.uniform(0.9, 1.1)
        
        # Update plant metrics with growth and variation, respecting maximum limits
        new_height = self.height + (height_growth * variation)
        new_root_length = self.root_length + (root_growth * variation)
        new_flowers = self.flowers + (flower_growth * variation)
        
        # Apply maximum limits
        self.height = min(new_height, PLANT_PARAMS["max_height"])
        self.root_length = min(new_root_length, PLANT_PARAMS["max_root_length"])
        self.flowers = min(round(new_flowers), PLANT_PARAMS["max_flowers"])
        
        # Update appearance based on environmental conditions and current phase
        self._update_appearance(environment, phase)
        
        # Store daily growth data
        self.daily_growth.append({
            "day": day,
            "phase": phase,
            "height": self.height,
            "root_length": self.root_length,
            "flowers": self.flowers,
            "appearance": self.appearance,
            "environment": environment.copy()
        })
        
    def _calculate_growth_factor(self, environment, phase):
        """
        Calculate overall growth factor based on how optimal the environment is
        Returns a value between 0 (poor conditions) and 1.2 (exceptional conditions)
        """
        # Start with a base growth factor
        growth_factor = 1.0
        self.stress_level = 0.0
        
        # Check temperature conditions
        temp_min, temp_max, temp_optimal = environment["temperature_range"]
        current_temp = environment["temperature"]
        
        if current_temp < temp_min:
            # Too cold
            temp_penalty = (temp_min - current_temp) / temp_min
            growth_factor -= temp_penalty * 0.5
            self.stress_level += temp_penalty * 0.3
        elif current_temp > temp_max:
            # Too hot
            temp_penalty = (current_temp - temp_max) / temp_max
            growth_factor -= temp_penalty * 0.6
            self.stress_level += temp_penalty * 0.4
        else:
            # Within range - check how close to optimal
            if temp_max == temp_min:
                temp_optimality = 1.0 if current_temp == temp_optimal else 0.8
            else:
                temp_optimality = 1 - abs(current_temp - temp_optimal) / (temp_max - temp_min)
            growth_factor += temp_optimality * 0.2
        
        # Check irrigation conditions
        irr_min, irr_max, irr_optimal = environment["irrigation_range"]
        current_irr = environment["irrigation"]
        
        if current_irr < irr_min:
            # Too dry
            irr_penalty = (irr_min - current_irr) / irr_min
            growth_factor -= irr_penalty * 0.7
            self.stress_level += irr_penalty * 0.5
        elif current_irr > irr_max:
            # Too wet
            irr_penalty = (current_irr - irr_max) / irr_max
            growth_factor -= irr_penalty * 0.6
            self.stress_level += irr_penalty * 0.4
        else:
            # Within range - check how close to optimal
            if irr_max == irr_min:
                irr_optimality = 1.0 if current_irr == irr_optimal else 0.8
            else:
                irr_optimality = 1 - abs(current_irr - irr_optimal) / (irr_max - irr_min)
            growth_factor += irr_optimality * 0.1
        
        # Check ventilation conditions
        vent_min, vent_max, vent_optimal = environment["ventilation_range"]
        current_vent = environment["ventilation"]
        
        if current_vent < vent_min:
            # Too little ventilation
            vent_penalty = (vent_min - current_vent) / vent_min
            growth_factor -= vent_penalty * 0.4
            self.stress_level += vent_penalty * 0.2
        elif current_vent > vent_max:
            # Too much ventilation
            vent_penalty = (current_vent - vent_max) / vent_max
            growth_factor -= vent_penalty * 0.3
            self.stress_level += vent_penalty * 0.1
        else:
            # Within range - check how close to optimal
            if vent_max == vent_min:
                vent_optimality = 1.0 if current_vent == vent_optimal else 0.8
            else:
                vent_optimality = 1 - abs(current_vent - vent_optimal) / (vent_max - vent_min)
            growth_factor += vent_optimality * 0.1
        
        # Check light conditions
        light_min, light_max, light_optimal = environment["light_hours_range"]
        current_light = environment["light_hours"]
        
        if current_light < light_min:
            # Too little light
            light_penalty = (light_min - current_light) / light_min
            growth_factor -= light_penalty * 0.6
            self.stress_level += light_penalty * 0.3
        elif current_light > light_max:
            # Too much light
            light_penalty = (current_light - light_max) / light_max
            growth_factor -= light_penalty * 0.3
            self.stress_level += light_penalty * 0.2
        else:
            # Within range - check how close to optimal
            if light_max == light_min:
                light_optimality = 1.0 if current_light == light_optimal else 0.8
            else:
                light_optimality = 1 - abs(current_light - light_optimal) / (light_max - light_min)
            growth_factor += light_optimality * 0.2
        
        # Ensure growth factor stays within reasonable bounds
        growth_factor = max(0.1, min(growth_factor, 1.2))
        self.stress_level = min(self.stress_level, 1.0)
        
        return growth_factor
    
    def _update_appearance(self, environment, phase):
        """Update the plant's appearance rating based on conditions and phase"""
        # Base appearance range for the current phase
        min_appearance, max_appearance = APPEARANCE_RATINGS[phase]
        
        # Calculate appearance modifier based on stress level
        appearance_mod = 1.0 - self.stress_level
        
        # Calculate base appearance for the phase
        base_appearance = min_appearance + (max_appearance - min_appearance) * appearance_mod
        
        # Add some random variation for natural appearance changes
        variation = random.uniform(-0.3, 0.3)
        
        # Update appearance
        self.appearance = round(max(0, min(10, base_appearance + variation)), 1)
    
    def get_status_description(self):
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
    
    def get_current_metrics(self):
        """Return the current growth metrics"""
        return {
            "plant_id": self.plant_id,
            "height": round(self.height, 1),
            "root_length": round(self.root_length, 1),
            "flowers": self.flowers,
            "appearance": self.appearance,
            "status": self.get_status_description()
        }


class GrowthSimulator:
    """Class to simulate growth of multiple flax plants"""
    
    def __init__(self, num_plants=1):
        """Initialize the growth simulator with a number of plants"""
        self.plants = [FlaxPlant(i+1) for i in range(num_plants)]
        self.current_day = 0
    
    def simulate_day(self, environment):
        """Simulate one day of growth for all plants"""
        self.current_day += 1
        
        for plant in self.plants:
            plant.update_growth(self.current_day, environment)
        
        return {
            "day": self.current_day,
            "phase": get_current_phase(self.current_day),
            "plants": [plant.get_current_metrics() for plant in self.plants]
        }
    
    def get_average_metrics(self):
        """Get average growth metrics across all plants"""
        total_height = sum(plant.height for plant in self.plants)
        total_roots = sum(plant.root_length for plant in self.plants)
        total_flowers = sum(plant.flowers for plant in self.plants)
        total_appearance = sum(plant.appearance for plant in self.plants)
        
        return {
            "day": self.current_day,
            "phase": get_current_phase(self.current_day),
            "avg_height": round(total_height / len(self.plants), 1),
            "avg_root_length": round(total_roots / len(self.plants), 1),
            "avg_flowers": round(total_flowers / len(self.plants), 1),
            "avg_appearance": round(total_appearance / len(self.plants), 1)
        }
