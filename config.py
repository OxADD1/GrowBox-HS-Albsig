# Configuration parameters for flax greenhouse simulation
import random

# Growth phase timelines (days)
GERMINATION_PHASE = (1, 10)  # Days 1-10
GROWTH_PHASE = (11, 60)      # Days 11-60
FLOWERING_PHASE = (61, 75)   # Days 61-75
RIPENING_PHASE = (76, 100)   # Days 76-100
TOTAL_DAYS = 100

# Environmental parameters by phase
# Format: (min, max, optimal)
ENVIRONMENT_PARAMS = {
    "germination": {
        "temperature": (15, 20, 18),         # °C
        "ventilation": (1, 2, 1.5),          # times per hour
        "irrigation": (50, 100, 75),         # ml per plant
        "light_hours": (12, 14, 13)          # hours per day
    },
    "growth": {
        "temperature": (18, 22, 20),
        "ventilation": (2, 3, 2.5),
        "irrigation": (100, 200, 150),
        "light_hours": (14, 16, 15)
    },
    "flowering": {
        "temperature": (20, 24, 22),
        "ventilation": (3, 4, 3.5),
        "irrigation": (150, 250, 200),
        "light_hours": (14, 14, 14)
    },
    "ripening": {
        "temperature": (18, 22, 20),
        "ventilation": (2, 3, 2.5),
        "irrigation": (100, 200, 150),
        "light_hours": (12, 14, 13)
    }
}

# Plant growth parameters
PLANT_PARAMS = {
    "max_height": 120,         # Maximum plant height in cm
    "max_root_length": 120,    # Maximum root length in cm
    "max_flowers": 50,         # Maximum number of flowers
    
    # Growth rate factors for different phases (relative values)
    "height_growth_factors": {
        "germination": 0.05,   # 5% of total growth in germination
        "growth": 0.70,        # 70% of total growth in growth phase
        "flowering": 0.20,     # 20% in flowering phase
        "ripening": 0.05       # 5% in ripening phase
    },
    
    "root_growth_factors": {
        "germination": 0.15,   # 15% of total growth in germination
        "growth": 0.65,        # 65% of total growth in growth phase
        "flowering": 0.15,     # 15% in flowering phase
        "ripening": 0.05       # 5% in ripening phase
    },
    
    "flower_growth_factors": {
        "germination": 0.0,    # 0% in germination
        "growth": 0.0,         # 0% in growth
        "flowering": 0.80,     # 80% in flowering
        "ripening": 0.20       # 20% in ripening
    }
}

# Appearance ratings (0-10 scale)
APPEARANCE_RATINGS = {
    "germination": (2, 4),     # Min, max appearance during germination
    "growth": (5, 8),
    "flowering": (7, 10),
    "ripening": (6, 9)
}

# Error simulation settings
ERROR_SIMULATION = {
    "probability": 0.1,        # 10% chance of suboptimal conditions each day
    "severity": {
        "temperature": 3,      # Maximum deviation from optimal range (°C)
        "ventilation": 0.5,    # Maximum deviation from optimal range (times/hr)
        "irrigation": 30,      # Maximum deviation from optimal range (ml)
        "light_hours": 2       # Maximum deviation from optimal range (hours)
    }
}

# Data storage settings
DATA_STORAGE = {
    "filename": "flax_simulation_data.csv",
    "directory": "data"
}

# Visualization settings
VISUALIZATION = {
    "colors": {
        "plant": "#228B22",        # Forest Green
        "root": "#8B4513",         # Saddle Brown
        "flower": "#FFD700",       # Gold
        "temperature": "#FF6347",  # Tomato
        "ventilation": "#1E90FF",  # Dodger Blue
        "irrigation": "#4682B4",   # Steel Blue
        "light": "#FFA500"         # Orange
    },
    "update_interval": 0.1         # seconds between visualization updates
}

def get_random_parameter(param_range):
    """Generate a random value within the specified parameter range"""
    min_val, max_val = param_range
    return round(random.uniform(min_val, max_val), 1)

def get_current_phase(day):
    """Determine the current growth phase based on the day"""
    if GERMINATION_PHASE[0] <= day <= GERMINATION_PHASE[1]:
        return "germination"
    elif GROWTH_PHASE[0] <= day <= GROWTH_PHASE[1]:
        return "growth"
    elif FLOWERING_PHASE[0] <= day <= FLOWERING_PHASE[1]:
        return "flowering"
    elif RIPENING_PHASE[0] <= day <= RIPENING_PHASE[1]:
        return "ripening"
    else:
        return "unknown"

def get_phase_day(day, phase):
    """Get the day number within the current phase"""
    if phase == "germination":
        return day - GERMINATION_PHASE[0] + 1
    elif phase == "growth":
        return day - GROWTH_PHASE[0] + 1
    elif phase == "flowering":
        return day - FLOWERING_PHASE[0] + 1
    elif phase == "ripening":
        return day - RIPENING_PHASE[0] + 1
    else:
        return 0

def get_phase_length(phase):
    """Get the total number of days in the specified phase"""
    if phase == "germination":
        return GERMINATION_PHASE[1] - GERMINATION_PHASE[0] + 1
    elif phase == "growth":
        return GROWTH_PHASE[1] - GROWTH_PHASE[0] + 1
    elif phase == "flowering":
        return FLOWERING_PHASE[1] - FLOWERING_PHASE[0] + 1
    elif phase == "ripening":
        return RIPENING_PHASE[1] - RIPENING_PHASE[0] + 1
    else:
        return 0
