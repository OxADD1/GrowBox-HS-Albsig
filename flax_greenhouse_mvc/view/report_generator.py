import os
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

class ReportGenerator:
    """Generates reports from greenhouse data"""
    
    def __init__(self, save_path="reports"):
        """Initialize the report generator"""
        self.save_path = save_path
        
        # Create save directory if it doesn't exist
        os.makedirs(save_path, exist_ok=True)
    
    def generate_daily_report(self, day_data, filename=None):
        """Generate a daily report for a specific day"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.save_path, f"daily_report_day{day_data['day']:03d}_{timestamp}.html")
        
        # Create HTML report
        html = self._generate_daily_html(day_data)
        
        # Save to file
        with open(filename, 'w') as f:
            f.write(html)
        
        return filename
    
    def generate_summary_report(self, all_data, filename=None):
        """Generate a summary report for the entire simulation"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.save_path, f"summary_report_{timestamp}.html")
        
        # Create HTML report
        html = self._generate_summary_html(all_data)
        
        # Save to file
        with open(filename, 'w') as f:
            f.write(html)
        
        return filename
    
    def _generate_daily_html(self, day_data):
        """Generate HTML for daily report"""
        day = day_data.get("day", 0)
        phase = day_data.get("phase", "unknown").capitalize()
        
        # Get plant data
        plant = day_data.get("plants_data", [{}])[0]
        height = plant.get("height", 0)
        root_length = plant.get("root_length", 0)
        flowers = plant.get("flowers", 0)
        appearance = plant.get("appearance", 0)
        status = plant.get("status", "Unknown")
        
        # Get environment data
        env = day_data.get("environment", {})
        temp = env.get("temperature", 0)
        soil_temp = env.get("soil_temperature", 0)
        ventilation = env.get("ventilation", 0)
        irrigation = env.get("irrigation", 0)
        light_hours = env.get("light_hours", 0)
        soil_moisture = env.get("soil_moisture", 0)
        
        # Create HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Daily Report - Day {day}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2 {{ color: #228B22; }}
                .section {{ margin: 20px 0; padding: 10px; border: 1px solid #ddd; }}
                .metrics {{ display: flex; flex-wrap: wrap; }}
                .metric {{ flex: 1; min-width: 200px; margin: 10px; padding: 15px; background-color: #f9f9f9; }}
                .value {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
                .unit {{ font-size: 14px; color: #666; }}
                .status {{ padding: 5px 10px; border-radius: 5px; display: inline-block; }}
                .optimal {{ background-color: #b3ffb3; }}
                .warning {{ background-color: #fff4b3; }}
                .error {{ background-color: #ffb3b3; }}
            </style>
        </head>
        <body>
            <h1>Flax Greenhouse - Daily Report</h1>
            
            <div class="section">
                <h2>Day {day} - {phase} Phase</h2>
                <p>Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <div class="section">
                <h2>Plant Metrics</h2>
                <div class="metrics">
                    <div class="metric">
                        <h3>Height</h3>
                        <div class="value">{height:.1f}<span class="unit">cm</span></div>
                    </div>
                    <div class="metric">
                        <h3>Root Length</h3>
                        <div class="value">{root_length:.1f}<span class="unit">cm</span></div>
                    </div>
                    <div class="metric">
                        <h3>Flowers</h3>
                        <div class="value">{flowers}</div>
                    </div>
                    <div class="metric">
                        <h3>Appearance</h3>
                        <div class="value">{appearance:.1f}<span class="unit">/10</span></div>
                        <div class="status {'optimal' if appearance >= 7 else 'warning' if appearance >= 4 else 'error'}">{status}</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Environmental Conditions</h2>
                <div class="metrics">
                    <div class="metric">
                        <h3>Air Temperature</h3>
                        <div class="value">{temp:.1f}<span class="unit">°C</span></div>
                    </div>
                    <div class="metric">
                        <h3>Soil Temperature</h3>
                        <div class="value">{soil_temp:.1f}<span class="unit">°C</span></div>
                    </div>
                    <div class="metric">
                        <h3>Ventilation</h3>
                        <div class="value">{ventilation:.1f}<span class="unit">/hr</span></div>
                    </div>
                    <div class="metric">
                        <h3>Irrigation</h3>
                        <div class="value">{irrigation:.1f}<span class="unit">ml</span></div>
                    </div>
                    <div class="metric">
                        <h3>Light Hours</h3>
                        <div class="value">{light_hours:.1f}<span class="unit">hrs</span></div>
                    </div>
                    <div class="metric">
                        <h3>Soil Moisture</h3>
                        <div class="value">{soil_moisture:.1f}<span class="unit">%</span></div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_summary_html(self, all_data):
        """Generate HTML for summary report"""
        if not all_data:
            return "<html><body><h1>No data available</h1></body></html>"
        
        # Get total days
        total_days = len(all_data)
        
        # Get final plant metrics
        final_data = all_data[-1]
        final_plant = final_data.get("plants_data", [{}])[0]
        final_height = final_plant.get("height", 0)
        final_root = final_plant.get("root_length", 0)
        final_flowers = final_plant.get("flowers", 0)
        final_appearance = final_plant.get("appearance", 0)
        
        # Calculate growth rates
        growth_phases = ["germination", "growth", "flowering", "ripening"]
        phase_data = {p: {"days": 0, "height_growth": 0, "root_growth": 0, "flower_growth": 0} for p in growth_phases}
        
        # Group data by phase
        for i in range(1, len(all_data)):
            prev_data = all_data[i-1]
            curr_data = all_data[i]
            
            phase = curr_data.get("phase", "unknown")
            if phase not in growth_phases:
                continue
                
            # Count days
            phase_data[phase]["days"] += 1
            
            # Calculate growth
            prev_plant = prev_data.get("plants_data", [{}])[0]
            curr_plant = curr_data.get("plants_data", [{}])[0]
            
            height_growth = curr_plant.get("height", 0) - prev_plant.get("height", 0)
            root_growth = curr_plant.get("root_length", 0) - prev_plant.get("root_length", 0)
            flower_growth = curr_plant.get("flowers", 0) - prev_plant.get("flowers", 0)
            
            phase_data[phase]["height_growth"] += height_growth
            phase_data[phase]["root_growth"] += root_growth
            phase_data[phase]["flower_growth"] += flower_growth
        
        # Calculate averages
        for phase in growth_phases:
            days = phase_data[phase]["days"]
            if days > 0:
                phase_data[phase]["height_growth"] /= days
                phase_data[phase]["root_growth"] /= days
                phase_data[phase]["flower_growth"] /= days
        
        # Create HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Flax Greenhouse - Summary Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2 {{ color: #228B22; }}
                .section {{ margin: 20px 0; padding: 10px; border: 1px solid #ddd; }}
                .metrics {{ display: flex; flex-wrap: wrap; }}
                .metric {{ flex: 1; min-width: 200px; margin: 10px; padding: 15px; background-color: #f9f9f9; }}
                .value {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
                .unit {{ font-size: 14px; color: #666; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
            </style>
        </head>
        <body>
            <h1>Flax Greenhouse - Summary Report</h1>
            
            <div class="section">
                <h2>Simulation Overview</h2>
                <p>Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                <p>Total Simulation Days: {total_days}</p>
            </div>
            
            <div class="section">
                <h2>Final Plant Metrics</h2>
                <div class="metrics">
                    <div class="metric">
                        <h3>Final Height</h3>
                        <div class="value">{final_height:.1f}<span class="unit">cm</span></div>
                    </div>
                    <div class="metric">
                        <h3>Final Root Length</h3>
                        <div class="value">{final_root:.1f}<span class="unit">cm</span></div>
                    </div>
                    <div class="metric">
                        <h3>Final Flowers</h3>
                        <div class="value">{final_flowers}</div>
                    </div>
                    <div class="metric">
                        <h3>Final Appearance</h3>
                        <div class="value">{final_appearance:.1f}<span class="unit">/10</span></div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Growth Rates by Phase</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Phase</th>
                            <th>Days</th>
                            <th>Height Growth (cm/day)</th>
                            <th>Root Growth (cm/day)</th>
                            <th>Flower Growth (flowers/day)</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for phase in growth_phases:
            data = phase_data[phase]
            html += f"""
                        <tr>
                            <td>{phase.capitalize()}</td>
                            <td>{data["days"]}</td>
                            <td>{data["height_growth"]:.2f}</td>
                            <td>{data["root_growth"]:.2f}</td>
                            <td>{data["flower_growth"]:.2f}</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        return html
