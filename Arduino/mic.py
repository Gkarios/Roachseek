import serial
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from datetime import datetime

# Open Serial Port (adjust COM port or `/dev/ttyUSB0`)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

# MQTT setup
def on_disconnect(client, userdata, rc, properties=None):
    print("Disconnected from MQTT broker with result code", rc)

mqtt_client = mqtt.Client(client_id="cockroach_publisher", callback_api_version=CallbackAPIVersion.VERSION2)
mqtt_client.on_disconnect = on_disconnect
mqtt_client.connect("broker.hivemq.com", 1883, 60)

while True:
    line = ser.readline().decode().strip()
    if line:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload = f"{timestamp}, {line}"
        mqtt_client.publish("arduino/cockroaches", payload)
        print("Published:", payload)