import paho.mqtt.client as mqtt
import json
import time
import threading

class MQTTController:
    """Handles MQTT communication between laptop and grow box controller"""
    
    def __init__(self, broker="localhost", port=1883, client_id="greenhouse_controller"):
        """Initialize the MQTT controller"""
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.topic_prefix = "greenhouse/"
        self.client = mqtt.Client(client_id)
        self.callbacks = {}
        self.connected = False
        
        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        # Start in separate thread
        self.thread = threading.Thread(target=self._mqtt_loop, daemon=True)
    
    def start(self):
        """Connect to MQTT broker and start processing messages"""
        try:
            self.client.connect(self.broker, self.port, 60)
            self.thread.start()
            return True
        except Exception as e:
            print(f"MQTT connection error: {e}")
            return False
    
    def stop(self):
        """Disconnect from MQTT broker"""
        self.client.disconnect()
    
    def publish(self, subtopic, payload):
        """Publish a message to a specific topic"""
        topic = f"{self.topic_prefix}{subtopic}"
        if isinstance(payload, dict):
            payload = json.dumps(payload)
        self.client.publish(topic, payload, qos=1)
    
    def subscribe(self, subtopic, callback):
        """Subscribe to a topic with a callback function"""
        topic = f"{self.topic_prefix}{subtopic}"
        self.client.subscribe(topic)
        self.callbacks[topic] = callback
    
    def _mqtt_loop(self):
        """Run the MQTT client loop in a separate thread"""
        self.client.loop_forever()
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when MQTT connection is established"""
        if rc == 0:
            print("Connected to MQTT broker")
            self.connected = True
            # Resubscribe to all topics
            for topic in self.callbacks.keys():
                self.client.subscribe(topic)
        else:
            print(f"Failed to connect to MQTT broker with code {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback for when a message is received"""
        topic = msg.topic
        try:
            payload = json.loads(msg.payload.decode())
        except:
            payload = msg.payload.decode()
        
        # Call the appropriate callback function
        if topic in self.callbacks:
            self.callbacks[topic](payload)
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when MQTT connection is lost"""
        self.connected = False
        print(f"Disconnected from MQTT broker with code {rc}")
        if rc != 0:
            print("Unexpected disconnection. Attempting to reconnect...")
            self.client.reconnect()
