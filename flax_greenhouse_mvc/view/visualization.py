import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import numpy as np
from datetime import datetime

class Visualizer:
    """Handles visualization of greenhouse data"""
    
    def __init__(self, save_path="visuals"):
        """Initialize the visualizer"""
        self.save_path = save_path
        self.data_history = []
        self.fig = None
        self.axes = {}
        
        # Create save directory if it doesn't exist
        os.makedirs(save_path, exist_ok=True)
        
        # Set up visual styles
        plt.style.use('ggplot')
        self.colors = {
            "plant": "#228B22",         # Forest Green
            "root": "#8B4513",          # Saddle Brown
            "flower": "#FFD700",        # Gold
            "temperature": "#FF6347",   # Tomato
            "soil_temp": "#CD5C5C",     # Indian Red
            "ventilation": "#1E90FF",   # Dodger Blue
            "irrigation": "#4682B4",    # Steel Blue
            "moisture": "#00CED1",      # Dark Turquoise
            "light": "#FFA500"          # Orange
        }
    
    def add_data_point(self, data_point):
        """Add a data point to the visualization history"""
        self.data_history.append(data_point)
    
    def create_visualization(self, data=None, save=True):
        """Create a visualization of the current state"""
        # Use provided data or most recent data point
        if data is None:
            if not self.data_history:
                print("No data available for visualization")
                return None
            data = self.data_history[-1]
            
        # Create figure
        self.fig = plt.figure(figsize=(18, 10))
        gs = gridspec.GridSpec(2, 3, height_ratios=[1, 1.5])
        
        # Create axes for different components
        self.axes = {
            "plant": plt.subplot(gs[0, 0]),
            "environment": plt.subplot(gs[0, 1]),
            "status": plt.subplot(gs[0, 2]),
            "history": plt.subplot(gs[1, :])
        }
        
        # Draw components
        self._draw_plant(data)
        self._draw_environment(data)
        self._draw_status(data)
        self._draw_history()
        
        # Add title
        day = data.get("day", 0)
        phase = data.get("phase", "unknown")
        plt.suptitle(f"Flax Greenhouse - Day {day} ({phase.capitalize()} Phase)", fontsize=16)
        
        # Adjust layout
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        # Save if requested
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.save_path, f"greenhouse_status_day{day:03d}_{timestamp}.png")
            plt.savefig(filename, dpi=150)
            plt.close()
            return filename
        
        return self.fig
    
    def _draw_plant(self, data):
        """Draw a visual representation of the plant"""
        ax = self.axes["plant"]
        ax.clear()
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1.2, 1.2)
        ax.axis('off')
        
        # Extract plant metrics
        height = data.get("height", 0)
        root_length = data.get("root_length", 0)
        flowers = data.get("flowers", 0)
        appearance = data.get("appearance", 0)
        
        # Scale relative to maximum sizes
        max_height = 120  # cm
        max_root = 120    # cm
        rel_height = height / max_height
        rel_root = root_length / max_root
        
        # Draw soil line
        ax.axhline(y=0, color='#8B4513', linestyle='-', linewidth=2)
        
        # Draw roots
        self._draw_roots(ax, rel_root)
        
        # Draw stem
        stem_height = rel_height * 0.9  # Leave space for flowers
        stem_width = 0.05 + (0.05 * rel_height)  # Stem gets thicker as plant grows
        
        # Make stem slightly curved for realism
        x_stem = np.linspace(-0.02, 0.02, 100)
        y_stem = np.linspace(0, stem_height, 100)
        ax.plot(x_stem, y_stem, color=self.colors["plant"], linewidth=3 + (stem_width * 20))
        
        # Add leaves along the stem
        self._draw_leaves(ax, stem_height, rel_height)
        
        # Draw flowers if present
        if flowers > 0:
            self._draw_flowers(ax, stem_height, flowers)
        
        # Add title with metrics
        title = f"Plant Metrics\n"
        title += f"Height: {height:.1f}cm | Roots: {root_length:.1f}cm | Flowers: {flowers}"
        ax.set_title(title)
        
        # Add appearance indicator
        status_text = data.get("status", "Unknown")
        ax.text(0, -1.1, f"Appearance: {appearance}/10 - {status_text}", 
                ha='center', fontsize=10, 
                bbox=dict(facecolor='white', alpha=0.7, boxstyle='round'))
    
    def _draw_roots(self, ax, rel_root):
        """Draw the root system"""
        # Main tap root
        tap_root_length = rel_root * 0.9
        x_root = np.zeros(100)
        y_root = np.linspace(0, -tap_root_length, 100)
        ax.plot(x_root, y_root, color=self.colors["root"], linewidth=2)
        
        # Add lateral roots
        root_density = int(10 * rel_root)
        for i in range(root_density):
            # Starting point along the tap root
            start_y = -(np.random.random() * tap_root_length)
            # Root length and angle
            length = np.random.random() * 0.3 * rel_root
            angle = np.random.choice([-1, 1]) * np.random.random() * np.pi/3  # +/- 60 degrees
            
            # Calculate endpoint
            end_x = length * np.sin(angle)
            end_y = start_y - length * np.cos(angle)
            
            # Draw lateral root
            ax.plot([0, end_x], [start_y, end_y], 
                    color=self.colors["root"], linewidth=1.5 - (i * 0.05))
    
    def _draw_leaves(self, ax, stem_height, rel_height):
        """Draw leaves along the stem"""
        leaf_count = int(10 * rel_height)
        max_leaf_size = 0.15 * rel_height
        
        for i in range(leaf_count):
            # Position along stem
            y_pos = (i + 1) / (leaf_count + 1) * stem_height
            
            # Alternate sides for leaves
            x_dir = 1 if i % 2 == 0 else -1
            
            # Leaf size decreases near top
            leaf_size = max_leaf_size * (1 - (i / leaf_count) * 0.3)
            
            # Draw leaf (simple ellipse)
            leaf = patches.Ellipse((x_dir * (0.1 + 0.05 * rel_height), y_pos), 
                                  leaf_size, leaf_size/2, 
                                  angle=x_dir * 30, 
                                  facecolor=self.colors["plant"], 
                                  alpha=0.8)
            ax.add_patch(leaf)
    
    def _draw_flowers(self, ax, stem_height, flower_count):
        """Draw flowers at the top of the plant"""
        if flower_count <= 0:
            return
        
        # Scale number of visible flowers (max 10 flowers shown)
        visible_flowers = min(int(flower_count / 5) + 1, 10)
        
        for i in range(visible_flowers):
            # Random position near top of stem
            x_pos = np.random.normal(0, 0.1)
            y_pos = stem_height + np.random.random() * 0.2
            
            # Flower size based on total count
            flower_size = 0.05 + (0.05 * min(flower_count / 50, 1))
            
            # Draw flower (circle)
            flower = patches.Circle((x_pos, y_pos), flower_size, 
                                   facecolor=self.colors["flower"], 
                                   edgecolor='black', linewidth=0.5, 
                                   alpha=0.9)
            ax.add_patch(flower)
    
    def _draw_environment(self, data):
        """Draw the environmental parameters"""
        ax = self.axes["environment"]
        ax.clear()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 6)  # Increased to accommodate more parameters
        ax.axis('off')
        
        # Get environment data
        environment = data.get("environment", {})
        
        # Define parameters to display
        params = [
            {"name": "Air Temperature", "value": environment.get("temperature", 0), "unit": "°C", 
             "range": (15, 24), "color": self.colors["temperature"]},
            {"name": "Soil Temperature", "value": environment.get("soil_temperature", 0), "unit": "°C", 
             "range": (15, 22), "color": self.colors["soil_temp"]},
            {"name": "Ventilation", "value": environment.get("ventilation", 0), "unit": "/hr", 
             "range": (1, 4), "color": self.colors["ventilation"]},
            {"name": "Irrigation", "value": environment.get("irrigation", 0), "unit": "ml/day", 
             "range": (50, 250), "color": self.colors["irrigation"]},
            {"name": "Soil Moisture", "value": environment.get("soil_moisture", 0), "unit": "%", 
             "range": (50, 90), "color": self.colors["moisture"]},
            {"name": "Light", "value": environment.get("light_hours", 0), "unit": "hrs", 
             "range": (12, 16), "color": self.colors["light"]}
        ]
        
        # Draw parameter gauges
        for i, param in enumerate(params):
            y_pos = i + 0.5
            
            # Parameter name and value
            ax.text(0, y_pos, f"{param['name']}: {param['value']}{param['unit']}", 
                    va='center', ha='left', fontsize=10)
            
            # Bar background (parameter range)
            ax.barh(y_pos, 1, height=0.3, left=0.4, color='lightgray', alpha=0.3)
            
            # Calculate position within range
            min_val, max_val = param["range"]
            range_width = max_val - min_val
            if range_width > 0:
                rel_pos = (param["value"] - min_val) / range_width
                rel_pos = max(0, min(1, rel_pos))  # Clamp between 0-1
            else:
                rel_pos = 0.5
            
            # Bar for current value
            ax.barh(y_pos, rel_pos, height=0.3, left=0.4, color=param["color"])
            
            # Range markers
            ax.text(0.4, y_pos - 0.2, f"{min_val}", va='top', ha='center', fontsize=8)
            ax.text(1.4, y_pos - 0.2, f"{max_val}", va='top', ha='center', fontsize=8)
        
        # Add title
        ax.set_title(f"Environmental Parameters")
        
        # Add error warning if present
        error = data.get("error", False)
        if error:
            error_text = data.get("error_text", "Warning: Suboptimal conditions")
            ax.text(0.7, 0.1, error_text, 
                    transform=ax.transAxes, ha='center', va='center',
                    bbox=dict(facecolor='red', alpha=0.2), color='darkred', fontsize=10)
    
    def _draw_status(self, data):
        """Draw the current status summary"""
        ax = self.axes["status"]
        ax.clear()
        ax.axis('off')
        
        # Set title
        ax.set_title("System Status")
        
        # Growth phase information
        day = data.get("day", 0)
        phase = data.get("phase", "unknown")
        
        # Phase boundaries (from model configuration)
        phase_days = {
            "germination": (1, 10),
            "growth": (11, 60),
            "flowering": (61, 70),
            "ripening": (71, 80)
        }
        
        # Calculate days in phase and remaining
        if phase in phase_days:
            phase_start, phase_end = phase_days[phase]
            days_in_phase = day - phase_start + 1
            days_remaining = phase_end - day
            total_days_in_phase = phase_end - phase_start + 1
        else:
            days_in_phase = 0
            days_remaining = 0
            total_days_in_phase = 0
        
        # Phase progress text
        progress_text = (
            f"Current Phase: {phase.capitalize()}\n"
            f"Day {days_in_phase} of {total_days_in_phase}\n"
            f"{days_remaining} days remaining in phase\n"
            f"Total Progress: Day {day}/80"
        )
        
        ax.text(0.5, 0.9, progress_text, ha='center', va='top', fontsize=11,
                bbox=dict(facecolor='lightblue', alpha=0.2))
        
        # Overall progress bar
        ax.barh(0.7, day/80, height=0.05, color='green')
        ax.barh(0.7, 1, height=0.05, color='lightgray', alpha=0.3)
        ax.text(0, 0.7, "0", ha='center', va='center', fontsize=8)
        ax.text(1, 0.7, "80", ha='center', va='center', fontsize=8)
        ax.text(day/80, 0.7, f"{day}", ha='center', va='bottom', fontsize=9)
        
        # Phase timeline (highlight current phase)
        y_pos = 0.55
        for p, (start, end) in phase_days.items():
            phase_width = (end - start + 1) / 80
            phase_pos = start / 80
            
            # Draw phase segment
            color = 'green' if p == phase else 'lightgray'
            alpha = 0.8 if p == phase else 0.3
            ax.barh(y_pos, phase_width, height=0.05, left=phase_pos, color=color, alpha=alpha)
            
            # Add phase label
            ax.text(phase_pos + phase_width/2, y_pos - 0.05, p[0].upper(), 
                    ha='center', va='top', fontsize=8)
        
        # Hardware status
        hardware = data.get("hardware_state", {})
        hardware_text = "Hardware Status:\n"
        
        if "heating_mat" in hardware:
            state = "ON" if hardware["heating_mat"].get("state", False) else "OFF"
            value = hardware["heating_mat"].get("value", 0)
            hardware_text += f"Heating Mat: {state} ({value}%)\n"
            
        if "water_pump" in hardware:
            state = "ON" if hardware["water_pump"].get("state", False) else "OFF"
            value = hardware["water_pump"].get("value", 0)
            hardware_text += f"Water Pump: {state} ({value}%)\n"
            
        if "ventilation" in hardware:
            state = "ON" if hardware["ventilation"].get("state", False) else "OFF"
            value = hardware["ventilation"].get("value", 0)
            hardware_text += f"Ventilation: {state} ({value}%)\n"
            
        if "led_lights" in hardware:
            state = "ON" if hardware["led_lights"].get("state", False) else "OFF"
            value = hardware["led_lights"].get("value", 0)
            hardware_text += f"LED Lights: {state} ({value}%)"
        
        ax.text(0.5, 0.3, hardware_text, ha='center', va='center', fontsize=11,
                bbox=dict(facecolor='lightgreen', alpha=0.2))
    
    def _draw_history(self):
        """Draw the historical data graph"""
        ax = self.axes["history"]
        ax.clear()
        
        if len(self.data_history) < 2:
            ax.text(0.5, 0.5, "Insufficient data for history graph", 
                   ha='center', va='center', fontsize=12)
            ax.set_title("Growth History")
            return
        
        # Prepare data
        days = [d.get("day", i+1) for i, d in enumerate(self.data_history)]
        heights = [d.get("height", 0) for d in self.data_history]
        roots = [d.get("root_length", 0) for d in self.data_history]
        flowers = [d.get("flowers", 0) for d in self.data_history]
        
        # Environment data
        temps = [d.get("environment", {}).get("temperature", 0) for d in self.data_history]
        soil_temps = [d.get("environment", {}).get("soil_temperature", 0) for d in self.data_history]
        
        # Plot growth metrics
        ax.plot(days, heights, 'o-', color=self.colors["plant"], label="Height (cm)")
        ax.plot(days, roots, 'o-', color=self.colors["root"], label="Root Length (cm)")
        
        # Plot flowers on secondary axis if they exist
        if max(flowers) > 0:
            ax2 = ax.twinx()
            ax2.plot(days, flowers, 'o-', color=self.colors["flower"], label="Flowers")
            ax2.set_ylabel("Number of Flowers", color=self.colors["flower"])
            ax2.tick_params(axis='y', labelcolor=self.colors["flower"])
            ax2.set_ylim(0, 50 * 1.1)
        
        # Add phase background regions
        self._add_phase_regions(ax)
        
        # Customize plot
        ax.set_xlabel("Day")
        ax.set_ylabel("Length (cm)")
        ax.set_xlim(0.5, 80.5)
        ax.set_ylim(0, 120 * 1.1)
        ax.grid(True, alpha=0.3)
        
        # Add legend
        lines, labels = ax.get_legend_handles_labels()
        if max(flowers) > 0:
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines + lines2, labels + labels2, loc='upper left')
        else:
            ax.legend(loc='upper left')
        
        # Set title
        ax.set_title("Growth History")
    
    def _add_phase_regions(self, ax):
        """Add background color regions for growth phases"""
        phases = [
            {"name": "Germination", "start": 1, "end": 10, "color": "lightyellow"},
            {"name": "Growth", "start": 11, "end": 60, "color": "lightgreen"},
            {"name": "Flowering", "start": 61, "end": 70, "color": "lavender"},
            {"name": "Ripening", "start": 71, "end": 80, "color": "wheat"}
        ]
        
        for phase in phases:
            ax.axvspan(phase["start"] - 0.5, phase["end"] + 0.5, 
                      alpha=0.2, color=phase["color"], 
                      label=phase["name"] if "name" in phase else None)
            
            # Add phase label
            mid_x = (phase["start"] + phase["end"]) / 2
            ax.text(mid_x, 0.02, phase["name"], transform=ax.transAxes,
                   ha='center', va='bottom', fontsize=9)
    
    def create_summary_charts(self, filename=None):
        """Create summary charts of all data"""
        if len(self.data_history) < 2:
            print("Insufficient data for summary charts")
            return None
        
        # Create figure with subplots
        fig, axs = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Growth curves (height, roots, flowers)
        ax1 = axs[0, 0]
        self._plot_growth_curves(ax1)
        
        # 2. Environmental parameters
        ax2 = axs[0, 1]
        self._plot_environmental_parameters(ax2)
        
        # 3. Growth rates by phase
        ax3 = axs[1, 0]
        self._plot_growth_rates_by_phase(ax3)
        
        # 4. Soil vs Air temperature comparison
        ax4 = axs[1, 1]
        self._plot_soil_vs_air_temperature(ax4)
        
        # Add title
        plt.suptitle("Flax Plant Growth Simulation Summary", fontsize=16)
        
        # Adjust layout
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        # Save figure
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.save_path, f"summary_charts_{timestamp}.png")
        plt.savefig(filename, dpi=150)
        plt.close()
        
        return filename
    
    def _plot_growth_curves(self, ax):
        """Plot growth curves for height, roots, and flowers"""
        days = [d.get("day", i+1) for i, d in enumerate(self.data_history)]
        heights = [d.get("height", 0) for d in self.data_history]
        roots = [d.get("root_length", 0) for d in self.data_history]
        flowers = [d.get("flowers", 0) for d in self.data_history]
        
        # Plot data
        ax.plot(days, heights, 'o-', color=self.colors["plant"], label="Height (cm)")
        ax.plot(days, roots, 'o-', color=self.colors["root"], label="Root Length (cm)")
        
        # Plot flowers on secondary axis
        if max(flowers) > 0:
            ax2 = ax.twinx()
            ax2.plot(days, flowers, 'o-', color=self.colors["flower"], label="Flowers")
            ax2.set_ylabel("Number of Flowers", color=self.colors["flower"])
            ax2.tick_params(axis='y', labelcolor=self.colors["flower"])
        
        # Add phase regions
        self._add_phase_regions(ax)
        
        # Customize plot
        ax.set_xlabel("Day")
        ax.set_ylabel("Length (cm)")
        ax.set_title("Plant Growth Over Time")
        ax.grid(True, alpha=0.3)
        
        # Add legend
        lines, labels = ax.get_legend_handles_labels()
        if max(flowers) > 0:
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines + lines2, labels + labels2, loc='upper left')
        else:
            ax.legend(loc='upper left')
    
    def _plot_environmental_parameters(self, ax):
        """Plot environmental parameters over time"""
        days = [d.get("day", i+1) for i, d in enumerate(self.data_history)]
        
        # Extract environment data
        temps = [d.get("environment", {}).get("temperature", 0) for d in self.data_history]
        vents = [d.get("environment", {}).get("ventilation", 0) for d in self.data_history]
        irrs = [d.get("environment", {}).get("irrigation", 0) for d in self.data_history]
        lights = [d.get("environment", {}).get("light_hours", 0) for d in self.data_history]
        
        # Create a second y-axis for irrigation
        ax2 = ax.twinx()
        
        # Plot temperature and light (left axis)
        ln1 = ax.plot(days, temps, '-', color=self.colors["temperature"], label="Temperature (°C)")
        ln2 = ax.plot(days, lights, '-', color=self.colors["light"], label="Light (hrs)")
        
        # Plot irrigation and ventilation (right axis)
        ln3 = ax2.plot(days, irrs, '-', color=self.colors["irrigation"], label="Irrigation (ml)")
        ln4 = ax2.plot(days, vents, '-', color=self.colors["ventilation"], label="Ventilation (/hr)")
        
        # Add phase regions
        self._add_phase_regions(ax)
        
        # Customize plot
        ax.set_xlabel("Day")
        ax.set_ylabel("Temperature (°C) / Light (hrs)")
        ax2.set_ylabel("Irrigation (ml) / Ventilation (/hr)")
        ax.set_title("Environmental Parameters Over Time")
        ax.grid(True, alpha=0.3)
        
        # Add legend
        lns = ln1 + ln2 + ln3 + ln4
        labs = [l.get_label() for l in lns]
        ax.legend(lns, labs, loc='upper right')
    
    def _plot_growth_rates_by_phase(self, ax):
        """Plot growth rates by phase"""
        # Define phases
        phases = ["germination", "growth", "flowering", "ripening"]
        phase_days = {
            "germination": (1, 10),
            "growth": (11, 60),
            "flowering": (61, 70),
            "ripening": (71, 80)
        }
        
        # Calculate growth rates for each phase
        growth_rates = {p: {"height": 0, "root": 0, "flowers": 0, "count": 0} for p in phases}
        
        for i in range(1, len(self.data_history)):
            prev = self.data_history[i-1]
            curr = self.data_history[i]
            
            day = curr.get("day", i+1)
            phase = next((p for p, (start, end) in phase_days.items() if start <= day <= end), None)
            
            if phase is None:
                continue
                
            # Daily growth
            height_growth = curr.get("height", 0) - prev.get("height", 0)
            root_growth = curr.get("root_length", 0) - prev.get("root_length", 0)
            flower_growth = curr.get("flowers", 0) - prev.get("flowers", 0)
            
            # Add to phase totals
            growth_rates[phase]["height"] += height_growth
            growth_rates[phase]["root"] += root_growth
            growth_rates[phase]["flowers"] += flower_growth
            growth_rates[phase]["count"] += 1
        
        # Calculate averages
        for phase in phases:
            count = growth_rates[phase]["count"]
            if count > 0:
                growth_rates[phase]["height"] /= count
                growth_rates[phase]["root"] /= count
                growth_rates[phase]["flowers"] /= count
        
        # Extract data for plotting
        heights = [growth_rates[p]["height"] for p in phases]
        roots = [growth_rates[p]["root"] for p in phases]
        flowers = [growth_rates[p]["flowers"] for p in phases]
        
        # Bar positions
        bar_width = 0.25
        r1 = np.arange(len(phases))
        r2 = [x + bar_width for x in r1]
        r3 = [x + bar_width for x in r2]
        
        # Create bars
        ax.bar(r1, heights, color=self.colors["plant"], width=bar_width, label='Height Growth (cm/day)')
        ax.bar(r2, roots, color=self.colors["root"], width=bar_width, label='Root Growth (cm/day)')
        ax.bar(r3, flowers, color=self.colors["flower"], width=bar_width, label='Flower Growth (flowers/day)')
        
        # Customize plot
        ax.set_xlabel('Growth Phase')
        ax.set_ylabel('Average Daily Growth')
        ax.set_title('Growth Rates by Phase')
        ax.set_xticks([r + bar_width for r in range(len(phases))])
        ax.set_xticklabels([p.capitalize() for p in phases])
        ax.legend()
    
    def _plot_soil_vs_air_temperature(self, ax):
        """Plot soil temperature vs air temperature"""
        days = [d.get("day", i+1) for i, d in enumerate(self.data_history)]
        
        # Extract temperature data
        air_temps = [d.get("environment", {}).get("temperature", 0) for d in self.data_history]
        soil_temps = [d.get("environment", {}).get("soil_temperature", 0) for d in self.data_history]
        
        # Plot temperatures
        ax.plot(days, air_temps, '-', color=self.colors["temperature"], label="Air Temperature (°C)")
        ax.plot(days, soil_temps, '-', color=self.colors["soil_temp"], label="Soil Temperature (°C)")
        
        # Calculate temperature difference
        temp_diff = [air - soil for air, soil in zip(air_temps, soil_temps)]
        ax2 = ax.twinx()
        ax2.plot(days, temp_diff, '--', color='purple', label="Temperature Difference")
        
        # Add phase regions
        self._add_phase_regions(ax)
        
        # Customize plot
        ax.set_xlabel("Day")
        ax.set_ylabel("Temperature (°C)")
        ax2.set_ylabel("Temperature Difference (°C)")
        ax.set_title("Soil vs Air Temperature")
        ax.grid(True, alpha=0.3)
        
        # Add legend
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines + lines2, labels + labels2, loc='upper right')
