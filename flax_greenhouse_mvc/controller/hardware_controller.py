import time
import threading

class HardwareController:
    """Controls physical hardware components of the greenhouse"""
    
    def __init__(self, simulation_mode=False):
        """Initialize the hardware controller"""
        self.simulation_mode = simulation_mode
        
        # Hardware components
        self.components = {
            "heating_mat": {"state": False, "value": 0},  # Temperature control
            "water_pump": {"state": False, "value": 0},   # Water flow control (ml/min)
            "ventilation": {"state": False, "value": 0},  # Fan speed (0-100%)
            "led_lights": {"state": False, "value": 0}    # Light intensity (0-100%)
        }
        
        # For tracking changes
        self.last_commands = {}
        self.command_queue = []
        self.lock = threading.Lock()
        
        # For hardware simulation
        if self.simulation_mode:
            self.simulator_thread = threading.Thread(target=self._simulate_hardware, daemon=True)
            self.simulator_running = False
    
    def initialize(self):
        """Initialize hardware connections or simulation"""
        if not self.simulation_mode:
            try:
                # Here you would initialize connection to your hardware
                # Example: self._init_gpio_pins()
                print("Hardware controller initialized with physical devices")
                return True
            except Exception as e:
                print(f"Error initializing hardware: {e}")
                print("Falling back to simulation mode")
                self.simulation_mode = True
        
        # Start hardware simulator if in simulation mode
        if self.simulation_mode:
            print("Hardware controller initialized in simulation mode")
            self.simulator_running = True
            self.simulator_thread.start()
        
        return True
    
    def set_component_state(self, component, state, value=None):
        """Set the state of a component"""
        if component not in self.components:
            print(f"Unknown component: {component}")
            return False
        
        with self.lock:
            command = {
                "component": component,
                "state": state,
                "value": value if value is not None else self.components[component]["value"],
                "timestamp": time.time()
            }
            self.command_queue.append(command)
        
        return True
    
    def process_commands(self):
        """Process all queued commands"""
        with self.lock:
            commands = self.command_queue.copy()
            self.command_queue = []
        
        for cmd in commands:
            self._execute_command(cmd)
    
    def get_component_state(self, component):
        """Get the current state of a component"""
        if component not in self.components:
            return None
        return self.components[component].copy()
    
    def _execute_command(self, command):
        """Execute a single hardware command"""
        component = command["component"]
        state = command["state"]
        value = command["value"]
        
        if self.simulation_mode:
            # Just update our internal state in simulation mode
            self.components[component]["state"] = state
            self.components[component]["value"] = value
            print(f"SIMULATION: {component} set to {'ON' if state else 'OFF'} with value {value}")
        else:
            # Here you would send commands to your physical hardware
            # Example: if component == "heating_mat": self._set_heating_mat(state, value)
            
            # Then update our internal state
            self.components[component]["state"] = state
            self.components[component]["value"] = value
        
        # Record the last command for each component
        self.last_commands[component] = command
    
    def _simulate_hardware(self):
        """Simulate hardware behavior (for testing without hardware)"""
        while self.simulator_running:
            # Process any pending commands
            self.process_commands()
            
            # Simulate hardware behavior over time
            # (e.g., temperature changes based on heating mat)
            
            # Sleep a bit to avoid consuming too much CPU
            time.sleep(0.1)
    
    def shutdown(self):
        """Safely shut down all hardware components"""
        # Turn off all components
        for component in self.components:
            self.set_component_state(component, False, 0)
        
        # Process the shutdown commands
        self.process_commands()
        
        # Stop the simulator if running
        if self.simulation_mode:
            self.simulator_running = False
            self.simulator_thread.join(timeout=1.0)
        
        print("Hardware controller shut down")
