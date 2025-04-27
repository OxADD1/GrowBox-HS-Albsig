# Data storage module for flax greenhouse simulation
import os
import csv
import json
import datetime
from config import DATA_STORAGE

class DataLogger:
    """Logs and stores simulation data"""
    
    def __init__(self, num_plants=1):
        """Initialize the data logger"""
        self.num_plants = num_plants
        self.simulation_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.data_dir = DATA_STORAGE["directory"]
        self.data_file = os.path.join(self.data_dir, f"{self.simulation_id}_{DATA_STORAGE['filename']}")
        self.daily_data = []
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize CSV file with headers
        self._initialize_csv()
    
    def _initialize_csv(self):
        """Initialize the CSV file with headers"""
        with open(self.data_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Basic headers
            headers = ["day", "date_time", "phase", 
                      "temperature", "ventilation", "irrigation", "light_hours"]
            
            # Add plant-specific headers
            for p in range(1, self.num_plants + 1):
                plant_headers = [
                    f"plant{p}_height",
                    f"plant{p}_root_length",
                    f"plant{p}_flowers",
                    f"plant{p}_appearance"
                ]
                headers.extend(plant_headers)
            
            # Add error status headers
            headers.extend(["error_active", "error_description"])
            
            writer.writerow(headers)
    
    def log_daily_data(self, day, phase, environment, plants_data, error_status):
        """
        Log data for a single simulation day
        
        Args:
            day: Current simulation day
            phase: Current growth phase
            environment: Dictionary of environmental parameters
            plants_data: List of plant metrics
            error_status: Dictionary with error information
        """
        # Create data entry
        entry = {
            "day": day,
            "date_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "phase": phase,
            "environment": environment,
            "plants_data": plants_data,
            "error_status": error_status
        }
        
        # Store in memory
        self.daily_data.append(entry)
        
        # Write to CSV
        self._write_to_csv(entry)
        
        return entry
    
    def _write_to_csv(self, entry):
        """Write a single data entry to the CSV file"""
        with open(self.data_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Prepare row data
            row = [
                entry["day"],
                entry["date_time"],
                entry["phase"],
                entry["environment"]["temperature"],
                entry["environment"]["ventilation"],
                entry["environment"]["irrigation"],
                entry["environment"]["light_hours"]
            ]
            
            # Add plant data
            for plant in entry["plants_data"]:
                row.extend([
                    plant["height"],
                    plant["root_length"],
                    plant["flowers"],
                    plant["appearance"]
                ])
            
            # Add error status
            row.extend([
                entry["error_status"]["error_active"],
                entry["error_status"]["error_description"]
            ])
            
            writer.writerow(row)
    
    def save_summary(self):
        """Save a summary of the simulation data"""
        summary_file = os.path.join(self.data_dir, f"{self.simulation_id}_summary.json")
        
        # Calculate summary statistics
        summary = self._calculate_summary()
        
        # Save to JSON file
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=4)
        
        return summary
    
    def _calculate_summary(self):
        """Calculate summary statistics from the simulation data"""
        phases = ["germination", "growth", "flowering", "ripening"]
        summary = {
            "simulation_id": self.simulation_id,
            "num_plants": self.num_plants,
            "total_days": len(self.daily_data),
            "phases": {},
            "plants": {},
            "errors": {
                "total": 0,
                "by_type": {
                    "temperature": 0,
                    "ventilation": 0,
                    "irrigation": 0,
                    "light_hours": 0
                }
            }
        }
        
        # Initialize plant data
        for p in range(1, self.num_plants + 1):
            summary["plants"][f"plant{p}"] = {
                "final_height": 0,
                "final_root_length": 0,
                "final_flowers": 0,
                "final_appearance": 0,
                "growth_rate": {
                    "height": 0,
                    "root": 0,
                    "flowers": 0
                }
            }
        
        # Initialize phase data
        for phase in phases:
            summary["phases"][phase] = {
                "days": 0,
                "avg_temperature": 0,
                "avg_ventilation": 0,
                "avg_irrigation": 0,
                "avg_light_hours": 0,
                "errors": 0
            }
        
        # Process daily data
        for entry in self.daily_data:
            phase = entry["phase"]
            
            # Skip if unknown phase
            if phase not in phases:
                continue
            
            # Update phase statistics
            summary["phases"][phase]["days"] += 1
            summary["phases"][phase]["avg_temperature"] += entry["environment"]["temperature"]
            summary["phases"][phase]["avg_ventilation"] += entry["environment"]["ventilation"]
            summary["phases"][phase]["avg_irrigation"] += entry["environment"]["irrigation"]
            summary["phases"][phase]["avg_light_hours"] += entry["environment"]["light_hours"]
            
            # Count errors
            if entry["error_status"]["error_active"]:
                summary["errors"]["total"] += 1
                summary["phases"][phase]["errors"] += 1
                
                # Categorize error
                error_desc = entry["error_status"]["error_description"].lower()
                if "temperature" in error_desc:
                    summary["errors"]["by_type"]["temperature"] += 1
                elif "ventilation" in error_desc:
                    summary["errors"]["by_type"]["ventilation"] += 1
                elif "irrigation" in error_desc:
                    summary["errors"]["by_type"]["irrigation"] += 1
                elif "light" in error_desc:
                    summary["errors"]["by_type"]["light_hours"] += 1
            
            # Update plant data for the last day
            if entry["day"] == len(self.daily_data):
                for i, plant in enumerate(entry["plants_data"]):
                    plant_key = f"plant{i+1}"
                    summary["plants"][plant_key]["final_height"] = plant["height"]
                    summary["plants"][plant_key]["final_root_length"] = plant["root_length"]
                    summary["plants"][plant_key]["final_flowers"] = plant["flowers"]
                    summary["plants"][plant_key]["final_appearance"] = plant["appearance"]
        
        # Calculate averages for phases
        for phase in phases:
            days = summary["phases"][phase]["days"]
            if days > 0:
                summary["phases"][phase]["avg_temperature"] /= days
                summary["phases"][phase]["avg_ventilation"] /= days
                summary["phases"][phase]["avg_irrigation"] /= days
                summary["phases"][phase]["avg_light_hours"] /= days
            
            # Round values
            summary["phases"][phase]["avg_temperature"] = round(summary["phases"][phase]["avg_temperature"], 1)
            summary["phases"][phase]["avg_ventilation"] = round(summary["phases"][phase]["avg_ventilation"], 1)
            summary["phases"][phase]["avg_irrigation"] = round(summary["phases"][phase]["avg_irrigation"], 1)
            summary["phases"][phase]["avg_light_hours"] = round(summary["phases"][phase]["avg_light_hours"], 1)
        
        # Calculate growth rates
        for p in range(1, self.num_plants + 1):
            plant_key = f"plant{p}"
            total_days = len(self.daily_data)
            
            if total_days > 0:
                first_day = self.daily_data[0]["plants_data"][p-1]
                last_day = self.daily_data[-1]["plants_data"][p-1]
                
                height_growth = last_day["height"] - first_day["height"]
                root_growth = last_day["root_length"] - first_day["root_length"]
                flower_growth = last_day["flowers"] - first_day["flowers"]
                
                summary["plants"][plant_key]["growth_rate"]["height"] = round(height_growth / total_days, 2)
                summary["plants"][plant_key]["growth_rate"]["root"] = round(root_growth / total_days, 2)
                summary["plants"][plant_key]["growth_rate"]["flowers"] = round(flower_growth / total_days, 2)
        
        return summary
    
    def get_all_data(self):
        """Return all logged data"""
        return self.daily_data
    
    def get_latest_data(self):
        """Return the most recent data entry"""
        if self.daily_data:
            return self.daily_data[-1]
        return None
    
    def get_data_file_path(self):
        """Return the path to the data file"""
        return self.data_file
