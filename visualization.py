# Visualization module for flax greenhouse simulation
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import numpy as np
from matplotlib.animation import FuncAnimation
from config import VISUALIZATION, get_current_phase, PLANT_PARAMS

class Visualizer:
    """Handles visualization of the greenhouse simulation"""
    
    def __init__(self, num_plants=1, save_path="visuals"):
        """Initialize the visualizer"""
        self.num_plants = num_plants
        self.save_path = save_path
        self.colors = VISUALIZATION["colors"]
        self.data_history = []
        
        # Create the save directory if it doesn't exist
        os.makedirs(save_path, exist_ok=True)
        
        # Initialize plot
        plt.style.use('ggplot')
        self.fig = None
        self.axes = None
    
    def update_data(self, day, phase, environment, plants_data, error_status):
        """Update visualization data"""
        # Store the data for history
        self.data_history.append({
            "day": day,
            "phase": phase,
            "environment": environment.copy(),
            "plants_data": plants_data.copy(),
            "error_status": error_status.copy()
        })
    
    def create_daily_visualization(self, day, save=True):
        """Create a visualization for a specific day"""
        # Get data for the day
        day_index = day - 1  # Convert to 0-based index
        if day_index < 0 or day_index >= len(self.data_history):
            print(f"No data available for day {day}")
            return None
        
        data = self.data_history[day_index]
        
        # Create figure
        self.fig = plt.figure(figsize=(18, 10))
        gs = gridspec.GridSpec(2, 3, height_ratios=[1, 1.5])
        
        # Plant visualization
        self.ax_plant = plt.subplot(gs[0, 0])
        self._draw_plant(data)
        
        # Environmental parameters
        self.ax_env = plt.subplot(gs[0, 1])
        self._draw_environmental_parameters(data)
        
        # Daily status
        self.ax_status = plt.subplot(gs[0, 2])
        self._draw_status(data)
        
        # Growth history
        self.ax_growth = plt.subplot(gs[1, :])
        self._draw_growth_history()
        
        # Adjust layout
        plt.tight_layout()
        
        # Save if requested
        if save:
            filename = os.path.join(self.save_path, f"day_{day:03d}.png")
            plt.savefig(filename, dpi=150)
            plt.close()
            return filename
        
        return self.fig
    
    def _draw_plant(self, data):
        """Draw a visual representation of the plant"""
        ax = self.ax_plant
        ax.clear()
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1.2, 1.2)
        ax.axis('off')
        
        # Get plant data (using first plant if multiple)
        plant = data["plants_data"][0]
        height = plant["height"]
        root_length = plant["root_length"]
        flowers = plant["flowers"]
        appearance = plant["appearance"]
        
        # Scale plant size relative to maximum
        rel_height = height / PLANT_PARAMS["max_height"]
        rel_root = root_length / PLANT_PARAMS["max_root_length"]
        
        # Draw soil line
        ax.axhline(y=0, color='#8B4513', linestyle='-', linewidth=2)
        
        # Draw roots
        self._draw_roots(ax, rel_root)
        
        # Draw stem
        stem_height = rel_height * 0.9  # Leave space for flowers
        stem_width = 0.05 + (0.05 * rel_height)  # Stem gets slightly thicker as plant grows
        
        # Make stem slightly curved for realism
        x_stem = np.linspace(-0.02, 0.02, 100)
        y_stem = np.linspace(0, stem_height, 100)
        ax.plot(x_stem, y_stem, color=self.colors["plant"], linewidth=3 + (stem_width * 20))
        
        # Add some leaves along the stem based on height
        self._draw_leaves(ax, stem_height, rel_height)
        
        # Draw flowers if in flowering or ripening phase
        if flowers > 0:
            self._draw_flowers(ax, stem_height, flowers)
        
        # Add title with metrics
        title = f"Day {data['day']} - {data['phase'].capitalize()} Phase\n"
        title += f"Height: {height:.1f}cm | Roots: {root_length:.1f}cm | Flowers: {flowers}"
        ax.set_title(title)
        
        # Add appearance indicator at bottom
        ax.text(0, -1.1, f"Appearance: {appearance}/10 - {plant['status']}", 
                ha='center', fontsize=10, 
                bbox=dict(facecolor='white', alpha=0.7, boxstyle='round'))
    
    def _draw_roots(self, ax, rel_root):
        """Draw the root system"""
        # Main tap root
        tap_root_length = rel_root * 0.9
        x_root = np.zeros(100)
        y_root = np.linspace(0, -tap_root_length, 100)
        ax.plot(x_root, y_root, color=self.colors["root"], linewidth=2)
        
        # Add some lateral roots
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
            flower_size = 0.05 + (0.05 * min(flower_count / PLANT_PARAMS["max_flowers"], 1))
            
            # Draw flower (circle)
            flower = patches.Circle((x_pos, y_pos), flower_size, 
                                   facecolor=self.colors["flower"], 
                                   edgecolor='black', linewidth=0.5, 
                                   alpha=0.9)
            ax.add_patch(flower)
    
    def _draw_environmental_parameters(self, data):
        """Draw the environmental parameters"""
        ax = self.ax_env
        ax.clear()
        
        # Get environment data
        env = data["environment"]
        phase = data["phase"]
        
        # Get parameter ranges for the current phase
        temp_range = env["temperature_range"]
        vent_range = env["ventilation_range"]
        irr_range = env["irrigation_range"]
        light_range = env["light_hours_range"]
        
        # Define parameters to display
        params = [
            {"name": "Temperature", "value": env["temperature"], "unit": "°C", 
             "range": (temp_range[0], temp_range[1]), "color": self.colors["temperature"]},
            {"name": "Ventilation", "value": env["ventilation"], "unit": "/hr", 
             "range": (vent_range[0], vent_range[1]), "color": self.colors["ventilation"]},
            {"name": "Irrigation", "value": env["irrigation"], "unit": "ml", 
             "range": (irr_range[0], irr_range[1]), "color": self.colors["irrigation"]},
            {"name": "Light", "value": env["light_hours"], "unit": "hrs", 
             "range": (light_range[0], light_range[1]), "color": self.colors["light"]}
        ]
        
        # Set up axes
        ax.set_xlim(0, 1)
        ax.set_ylim(0, len(params))
        ax.axis('off')
        
        # Draw parameter gauges
        for i, param in enumerate(params):
            y_pos = i + 0.5
            
            # Parameter name and value
            ax.text(0, y_pos, f"{param['name']}: {param['value']}{param['unit']}", 
                    va='center', ha='left', fontsize=12)
            
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
        ax.set_title(f"Environmental Parameters\n({phase.capitalize()} Phase)")
        
        # Add error warning if present
        if data["error_status"]["error_active"]:
            error_text = data["error_status"]["error_description"]
            ax.text(0.7, 0.1, f"WARNING: {error_text}", 
                    transform=ax.transAxes, ha='center', va='center',
                    bbox=dict(facecolor='red', alpha=0.2), color='darkred', fontsize=10)
    
    def _draw_status(self, data):
        """Draw the current status summary"""
        ax = self.ax_status
        ax.clear()
        ax.axis('off')
        
        # Set title
        ax.set_title("Growth Status")
        
        # Calculate days in current phase and days remaining
        day = data["day"]
        phase = data["phase"]
        
        # Determine phase boundaries
        phase_days = {
            "germination": (1, 10),
            "growth": (11, 60),
            "flowering": (61, 75),
            "ripening": (76, 100)
        }
        
        current_phase_start, current_phase_end = phase_days.get(phase, (0, 0))
        days_in_phase = day - current_phase_start + 1
        days_remaining = current_phase_end - day
        
        # Phase progress
        progress_text = (
            f"Current Phase: {phase.capitalize()}\n"
            f"Day {days_in_phase} of {current_phase_end - current_phase_start + 1}\n"
            f"{days_remaining} days remaining in phase\n"
            f"Total Progress: Day {day}/100"
        )
        
        ax.text(0.5, 0.9, progress_text, ha='center', va='top', fontsize=11,
                bbox=dict(facecolor='lightblue', alpha=0.2))
        
        # Overall progress bar
        ax.barh(0.7, day/100, height=0.05, color='green')
        ax.barh(0.7, 1, height=0.05, color='lightgray', alpha=0.3)
        ax.text(0, 0.7, "0", ha='center', va='center', fontsize=8)
        ax.text(1, 0.7, "100", ha='center', va='center', fontsize=8)
        ax.text(day/100, 0.7, f"{day}", ha='center', va='bottom', fontsize=9)
        
        # Phase progress (highlight current phase)
        y_pos = 0.55
        prev_end = 0
        
        for p, (start, end) in phase_days.items():
            phase_width = (end - start + 1) / 100
            phase_pos = start / 100
            
            # Draw phase segment
            color = 'green' if p == phase else 'lightgray'
            alpha = 0.8 if p == phase else 0.3
            ax.barh(y_pos, phase_width, height=0.05, left=phase_pos, color=color, alpha=alpha)
            
            # Add phase label
            ax.text(phase_pos + phase_width/2, y_pos - 0.05, p[0].upper(), 
                    ha='center', va='top', fontsize=8)
        
        # Add plant metrics
        plant = data["plants_data"][0]  # Using first plant
        metrics_text = (
            f"Plant Metrics:\n"
            f"Height: {plant['height']:.1f} cm\n"
            f"Root Length: {plant['root_length']:.1f} cm\n"
            f"Flowers: {plant['flowers']}\n"
            f"Appearance: {plant['appearance']}/10"
        )
        
        ax.text(0.5, 0.3, metrics_text, ha='center', va='center', fontsize=11,
                bbox=dict(facecolor='lightgreen', alpha=0.2))
    
    def _draw_growth_history(self):
        """Draw the growth history graph"""
        ax = self.ax_growth
        ax.clear()
        
        # Prepare data
        days = [d["day"] for d in self.data_history]
        
        # Get data for first plant
        heights = [d["plants_data"][0]["height"] for d in self.data_history]
        roots = [d["plants_data"][0]["root_length"] for d in self.data_history]
        flowers = [d["plants_data"][0]["flowers"] for d in self.data_history]
        
        # Environment data
        temps = [d["environment"]["temperature"] for d in self.data_history]
        irrigation = [d["environment"]["irrigation"] for d in self.data_history]
        light = [d["environment"]["light_hours"] for d in self.data_history]
        
        # Plot growth metrics
        ax.plot(days, heights, 'o-', color=self.colors["plant"], label="Height (cm)")
        ax.plot(days, roots, 'o-', color=self.colors["root"], label="Root Length (cm)")
        
        # Plot flowers on secondary axis if they exist
        if sum(flowers) > 0:
            ax2 = ax.twinx()
            ax2.plot(days, flowers, 'o-', color=self.colors["flower"], label="Flowers")
            ax2.set_ylabel("Number of Flowers", color=self.colors["flower"])
            ax2.tick_params(axis='y', labelcolor=self.colors["flower"])
            ax2.set_ylim(0, PLANT_PARAMS["max_flowers"] * 1.1)
        
        # Add growth phase background regions
        self._add_phase_regions(ax)
        
        # Customize plot
        ax.set_xlabel("Day")
        ax.set_ylabel("Length (cm)")
        ax.set_xlim(0.5, 100.5)
        ax.set_ylim(0, PLANT_PARAMS["max_height"] * 1.1)
        ax.grid(True, alpha=0.3)
        
        # Add legend
        lines, labels = ax.get_legend_handles_labels()
        if sum(flowers) > 0:
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines + lines2, labels + labels2, loc='upper left')
        else:
            ax.legend(loc='upper left')
        
        # Set title
        ax.set_title("Plant Growth History")
    
    def _add_phase_regions(self, ax):
        """Add background color regions for growth phases"""
        phases = [
            {"name": "Germination", "start": 1, "end": 10, "color": "lightyellow"},
            {"name": "Growth", "start": 11, "end": 60, "color": "lightgreen"},
            {"name": "Flowering", "start": 61, "end": 75, "color": "lavender"},
            {"name": "Ripening", "start": 76, "end": 100, "color": "wheat"}
        ]
        
        for phase in phases:
            ax.axvspan(phase["start"] - 0.5, phase["end"] + 0.5, 
                      alpha=0.2, color=phase["color"], 
                      label=phase["name"] if "name" in phase else None)
            
            # Add phase label
            mid_x = (phase["start"] + phase["end"]) / 2
            ax.text(mid_x, 0.02, phase["name"], transform=ax.transAxes,
                   ha='center', va='bottom', fontsize=9)
    
    def create_animation(self, fps=5, dpi=100):
        """Create an animation of the entire growth cycle"""
        # Initialize figure
        fig = plt.figure(figsize=(18, 10))
        gs = gridspec.GridSpec(2, 3, height_ratios=[1, 1.5])
        
        # Initialize subplots
        self.ax_plant = plt.subplot(gs[0, 0])
        self.ax_env = plt.subplot(gs[0, 1])
        self.ax_status = plt.subplot(gs[0, 2])
        self.ax_growth = plt.subplot(gs[1, :])
        
        # Define update function for animation
        def update(day_index):
            if day_index >= len(self.data_history):
                return
            
            data = self.data_history[day_index]
            
            # Update each subplot
            self._draw_plant(data)
            self._draw_environmental_parameters(data)
            self._draw_status(data)
            self._draw_growth_history()
            
            plt.tight_layout()
            return fig.canvas.draw_idle()
        
        # Create animation
        anim = FuncAnimation(fig, update, frames=len(self.data_history), interval=1000/fps)
        
        # Save animation
        filename = os.path.join(self.save_path, "growth_animation.mp4")
        anim.save(filename, dpi=dpi, writer='ffmpeg')
        plt.close()
        
        return filename
    
    def create_summary_charts(self):
        """Create summary charts for the entire simulation"""
        if not self.data_history:
            print("No data available for summary charts")
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
        
        # 4. Appearance over time
        ax4 = axs[1, 1]
        self._plot_appearance_over_time(ax4)
        
        # Add title
        plt.suptitle("Flax Plant Growth Simulation Summary", fontsize=16)
        
        # Adjust layout
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        # Save figure
        filename = os.path.join(self.save_path, "summary_charts.png")
        plt.savefig(filename, dpi=150)
        plt.close()
        
        return filename
    
    def _plot_growth_curves(self, ax):
        """Plot growth curves for height, roots, and flowers"""
        days = [d["day"] for d in self.data_history]
        heights = [d["plants_data"][0]["height"] for d in self.data_history]
        roots = [d["plants_data"][0]["root_length"] for d in self.data_history]
        flowers = [d["plants_data"][0]["flowers"] for d in self.data_history]
        
        # Plot data
        ax.plot(days, heights, 'o-', color=self.colors["plant"], label="Height (cm)")
        ax.plot(days, roots, 'o-', color=self.colors["root"], label="Root Length (cm)")
        
        # Plot flowers on secondary axis
        if sum(flowers) > 0:
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
        if sum(flowers) > 0:
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines + lines2, labels + labels2, loc='upper left')
        else:
            ax.legend(loc='upper left')
    
    def _plot_environmental_parameters(self, ax):
        """Plot environmental parameters over time"""
        days = [d["day"] for d in self.data_history]
        temps = [d["environment"]["temperature"] for d in self.data_history]
        vents = [d["environment"]["ventilation"] for d in self.data_history]
        irrs = [d["environment"]["irrigation"] for d in self.data_history]
        lights = [d["environment"]["light_hours"] for d in self.data_history]
        
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
        phases = ["germination", "growth", "flowering", "ripening"]
        phase_data = {p: {"height": [], "root": [], "flowers": []} for p in phases}
        
        # Group data by phase
        for i in range(1, len(self.data_history)):
            prev_data = self.data_history[i-1]
            curr_data = self.data_history[i]
            phase = curr_data["phase"]
            
            # Skip if unknown phase
            if phase not in phases:
                continue
            
            # Calculate daily growth
            height_growth = curr_data["plants_data"][0]["height"] - prev_data["plants_data"][0]["height"]
            root_growth = curr_data["plants_data"][0]["root_length"] - prev_data["plants_data"][0]["root_length"]
            flower_growth = curr_data["plants_data"][0]["flowers"] - prev_data["plants_data"][0]["flowers"]
            
            phase_data[phase]["height"].append(height_growth)
            phase_data[phase]["root"].append(root_growth)
            phase_data[phase]["flowers"].append(flower_growth)
        
        # Calculate average growth rates
        avg_height = [np.mean(phase_data[p]["height"]) if phase_data[p]["height"] else 0 for p in phases]
        avg_root = [np.mean(phase_data[p]["root"]) if phase_data[p]["root"] else 0 for p in phases]
        avg_flower = [np.mean(phase_data[p]["flowers"]) if phase_data[p]["flowers"] else 0 for p in phases]
        
        # Bar positions
        bar_width = 0.25
        r1 = np.arange(len(phases))
        r2 = [x + bar_width for x in r1]
        r3 = [x + bar_width for x in r2]
        
        # Create bars
        ax.bar(r1, avg_height, color=self.colors["plant"], width=bar_width, label='Height Growth (cm/day)')
        ax.bar(r2, avg_root, color=self.colors["root"], width=bar_width, label='Root Growth (cm/day)')
        ax.bar(r3, avg_flower, color=self.colors["flower"], width=bar_width, label='Flower Growth (flowers/day)')
        
        # Customize plot
        ax.set_xlabel('Growth Phase')
        ax.set_ylabel('Average Daily Growth')
        ax.set_title('Growth Rates by Phase')
        ax.set_xticks([r + bar_width for r in range(len(phases))])
        ax.set_xticklabels([p.capitalize() for p in phases])
        ax.legend()
    
    def _plot_appearance_over_time(self, ax):
        """Plot appearance rating over time"""
        days = [d["day"] for d in self.data_history]
        appearance = [d["plants_data"][0]["appearance"] for d in self.data_history]
        
        # Add error status
        error_days = [d["day"] for d in self.data_history if d["error_status"]["error_active"]]
        error_appearance = [d["plants_data"][0]["appearance"] for d in self.data_history if d["error_status"]["error_active"]]
        
        # Plot appearance
        ax.plot(days, appearance, '-', color='darkgreen', label="Appearance Rating")
        
        # Highlight error days
        if error_days:
            ax.scatter(error_days, error_appearance, color='red', s=50, label="Environmental Error")
        
        # Add phase regions
        self._add_phase_regions(ax)
        
        # Appearance zones
        ax.axhspan(8, 10, alpha=0.2, color='lightgreen', label='Thriving')
        ax.axhspan(6, 8, alpha=0.2, color='palegreen')
        ax.axhspan(4, 6, alpha=0.2, color='khaki')
        ax.axhspan(2, 4, alpha=0.2, color='lightsalmon')
        ax.axhspan(0, 2, alpha=0.2, color='lightcoral', label='Critical')
        
        # Customize plot
        ax.set_xlabel("Day")
        ax.set_ylabel("Appearance Rating (0-10)")
        ax.set_title("Plant Appearance Over Time")
        ax.set_ylim(0, 10)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='lower right')
