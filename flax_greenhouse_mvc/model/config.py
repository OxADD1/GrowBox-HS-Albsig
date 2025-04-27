# Configuration for flax plant growth model and greenhouse control

# 80-day growing cycle divided into phases
PHASES = {
    "germination": (1, 10),    # Days 1-10
    "growth": (11, 60),        # Days 11-60
    "flowering": (61, 70),     # Days 61-70
    "ripening": (71, 80)       # Days 71-80
}

# Optimal environmental conditions by phase
ENVIRONMENT = {
    "germination": {
        "temperature": (15, 20),       # °C
        "ventilation": (1, 2),         # times per hour
        "irrigation": (50, 100),       # ml per plant
        "light_hours": (12, 14)        # hours per day
    },
    "growth": {
        "temperature": (18, 22),
        "ventilation": (2, 3),
        "irrigation": (100, 200),
        "light_hours": (14, 16)
    },
    "flowering": {
        "temperature": (20, 24),
        "ventilation": (3, 4),
        "irrigation": (150, 250),
        "light_hours": (14, 14)
    },
    "ripening": {
        "temperature": (18, 22),
        "ventilation": (2, 3),
        "irrigation": (100, 200),
        "light_hours": (12, 14)
    }
}

# Maximum values for plant metrics
MAX_VALUES = {
    "height": 120,         # Maximum plant height in cm
    "root_length": 120,    # Maximum root length in cm
    "flowers": 50          # Maximum number of flowers
}

# Average daily growth rates by phase
GROWTH_RATES = {
    "germination": {
        "height": 0.4,     # cm per day
        "root": 1.2,       # cm per day
        "flowers": 0       # flowers per day
    },
    "growth": {
        "height": 1.0,
        "root": 1.0,
        "flowers": 0
    },
    "flowering": {
        "height": 1.2,
        "root": 0.6,
        "flowers": 2.5
    },
    "ripening": {
        "height": 0.2,
        "root": 0.2,
        "flowers": 0.2
    }
}

# Appearance ratings (0-10 scale) by phase
APPEARANCE_RATINGS = {
    "germination": (2, 4),     # Min, max appearance during germination
    "growth": (5, 8),
    "flowering": (7, 10),
    "ripening": (6, 9)
}

# MQTT configuration
MQTT_CONFIG = {
    "broker": "localhost",     # MQTT broker address
    "port": 1883,              # MQTT broker port
    "client_id": "greenhouse_controller"
}

# Sensor configuration
SENSOR_CONFIG = {
    "read_interval": 10,       # Seconds between sensor readings
    "data_dir": "data/sensor_data"
}

# Hardware configuration
HARDWARE_CONFIG = {
    "control_interval": 60,    # Seconds between hardware control adjustments
}
