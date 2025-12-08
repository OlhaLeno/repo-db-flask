import json
import time
import random
from datetime import datetime, timezone
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import threading

class SensorEmulator:
    def __init__(self, config_path='config.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.connection_string = self.config['service_bus']['connection_string']
        self.queue_name = self.config['service_bus']['queue_name']
        self.run_duration = self.config['run_duration_seconds']
        self.sensors = self.config['sensors']
        self.running = True
        
    def generate_sensor_data(self, sensor):
        """Generate sensor data"""
        value = random.uniform(
            sensor['value_range']['min'],
            sensor['value_range']['max']
        )
        
        return {
            'sensor_id': sensor['sensor_id'],
            'sensor_type': sensor['sensor_type'],
            'value': round(value, 2),
            'latitude': sensor['location']['latitude'],
            'longitude': sensor['location']['longitude'],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def send_to_queue(self, message):
        """Send message to Azure Service Bus Queue"""
        try:
            with ServiceBusClient.from_connection_string(self.connection_string) as client:
                with client.get_queue_sender(self.queue_name) as sender:
                    msg = ServiceBusMessage(json.dumps(message))
                    sender.send_messages(msg)
                    print(f"Sent: {message['sensor_id']} - {message['sensor_type']}: {message['value']}")
        except Exception as e:
            print(f"Error sending message: {e}")
    
    def run_sensor(self, sensor):
        """Run sensor emulation"""
        interval = sensor['interval_ms'] / 1000.0  # Convert to seconds
        end_time = time.time() + self.run_duration
        
        while self.running and time.time() < end_time:
            data = self.generate_sensor_data(sensor)
            self.send_to_queue(data)
            time.sleep(interval)
    
    def run(self):
        """Run all sensor emulation"""
        print("Starting IoT Sensor Emulator...")
        print(f"Running for {self.run_duration} seconds")
        
        threads = []
        for sensor in self.sensors:
            print(f"Started sensor: {sensor['sensor_id']} ({sensor['sensor_type']})")
            thread = threading.Thread(target=self.run_sensor, args=(sensor,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for completion or interrupt
        try:
            time.sleep(self.run_duration)
        except KeyboardInterrupt:
            print("\nStopping emulator...")
            self.running = False
        
        # Wait for threads to finish
        for thread in threads:
            thread.join(timeout=1)
        
        print("Emulator stopped.")

if __name__ == '__main__':
    emulator = SensorEmulator()
    emulator.run()

