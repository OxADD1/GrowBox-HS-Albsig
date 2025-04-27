# Main execution file for flax greenhouse simulation
import os
import time
import argparse
import matplotlib.pyplot as plt
from config import TOTAL_DAYS, VISUALIZATION, get_current_phase
from controller import EnvironmentController
from plant_simulator import GrowthSimulator
from data_storage import DataLogger
from visualization import Visualizer

def run_simulation(num_plants=1, interactive=False, save_interval=10, error_simulation=True):
    """
    Run the flax greenhouse simulation
    
    Args:
        num_plants: Number of plants to simulate
        interactive: Whether to show interactive visualizations
        save_interval: How often to save visualizations (in days)
        error_simulation: Whether to simulate random errors
    """
    print(f"Starting flax greenhouse simulation with {num_plants} plants...")
    
    # Initialize components
    controller = EnvironmentController(error_simulation=error_simulation)
    simulator = GrowthSimulator(num_plants=num_plants)
    data_logger = DataLogger(num_plants=num_plants)
    visualizer = Visualizer(num_plants=num_plants)
    
    # Main simulation loop
    for day in range(1, TOTAL_DAYS + 1):
        # Get current phase
        phase = get_current_phase(day)
        
        # Set environmental parameters for the day
        environment = controller.set_parameters_for_day(day)
        
        # Simulate plant growth
        growth_data = simulator.simulate_day(environment)
        
        # Get error status
        error_status = controller.get_error_status()
        
        # Log data
        data_logger.log_daily_data(
            day=day,
            phase=phase,
            environment=environment,
            plants_data=growth_data["plants"],
            error_status=error_status
        )
        
        # Update visualization data
        visualizer.update_data(
            day=day,
            phase=phase,
            environment=environment,
            plants_data=growth_data["plants"],
            error_status=error_status
        )
        
        # Display progress
        plant_metrics = growth_data["plants"][0]
        print(f"\nDay {day} ({phase.capitalize()} Phase):")
        print(f"  Height: {plant_metrics['height']:.1f}cm, Roots: {plant_metrics['root_length']:.1f}cm, Flowers: {plant_metrics['flowers']}")
        print(f"  Temperature: {environment['temperature']:.1f}°C, Irrigation: {environment['irrigation']:.1f}ml")
        print(f"  Ventilation: {environment['ventilation']:.1f}/hr, Light: {environment['light_hours']:.1f}hrs")
        
        if error_status["error_active"]:
            print(f"  WARNING: {error_status['error_description']}")
        
        print(f"  Plant Status: {plant_metrics['status']}")
        
        # Create visualization at specified intervals
        if day % save_interval == 0 or day == TOTAL_DAYS:
            print(f"  Creating visualization for day {day}...")
            if interactive:
                fig = visualizer.create_daily_visualization(day, save=True)
                plt.draw()
                plt.pause(VISUALIZATION["update_interval"])
            else:
                visualizer.create_daily_visualization(day, save=True)
        
        # Pause for better viewing
        if interactive:
            time.sleep(VISUALIZATION["update_interval"])
    
    # Create summary visualization
    print("\nCreating summary charts...")
    summary_file = visualizer.create_summary_charts()
    print(f"Summary charts saved to: {summary_file}")
    
    # Create animation
    print("Creating growth animation...")
    animation_file = visualizer.create_animation()
    print(f"Animation saved to: {animation_file}")
    
    # Save summary data
    print("Saving simulation summary...")
    summary = data_logger.save_summary()
    
    print(f"\nSimulation completed! Data saved to: {data_logger.get_data_file_path()}")
    
    # Display final results
    avg_metrics = simulator.get_average_metrics()
    print("\nFinal Plant Metrics:")
    print(f"  Average Height: {avg_metrics['avg_height']}cm")
    print(f"  Average Root Length: {avg_metrics['avg_root_length']}cm")
    print(f"  Average Flowers: {avg_metrics['avg_flowers']}")
    print(f"  Average Appearance: {avg_metrics['avg_appearance']}/10")
    
    # Return summary for analysis
    return summary

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Flax Greenhouse Simulation")
    parser.add_argument("--plants", type=int, default=1, help="Number of plants to simulate")
    parser.add_argument("--interactive", action="store_true", help="Show interactive visualizations")
    parser.add_argument("--save-interval", type=int, default=5, help="How often to save visualizations (in days)")
    parser.add_argument("--no-errors", action="store_true", help="Disable error simulation")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    run_simulation(
        num_plants=args.plants,
        interactive=args.interactive,
        save_interval=args.save_interval,
        error_simulation=not args.no_errors
    )
