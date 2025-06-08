from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from datetime import datetime
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///detections.db'
db = SQLAlchemy(app)
socketio = SocketIO(app, async_mode='threading')

class Detection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String, nullable=False)
    minute = db.Column(db.String, nullable=False)
    weather = db.Column(db.Float, nullable=True)  # in Celsius

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/histogram')
def histogram():
    results = db.session.query(
        db.func.substr(Detection.minute, 12, 2), db.func.count(Detection.id)
    ).group_by(db.func.substr(Detection.minute, 12, 2)).all()
    # Sort by hour as integer
    results = sorted([(int(hour), count) for hour, count in results])
    total = sum(count for _, count in results) or 1
    labels = [f"{hour:02d}" for hour, _ in results]
    data = [round((count / total) * 100) for _, count in results]
    raw = [count for _, count in results]
    return jsonify({"labels": labels, "data": data, "raw": raw})

@app.route('/histogram_temp')
def histogram_temp():
    # Group by rounded temperature (as integer)
    results = db.session.query(
        db.func.round(Detection.weather), db.func.count(Detection.id)
    ).group_by(db.func.round(Detection.weather)).all()
    # Remove None values (in case weather API failed)
    results = [(int(temp), count) for temp, count in results if temp is not None]
    results.sort()  # Sort by temperature ascending
    total = sum(count for _, count in results) or 1
    labels = [str(temp) for temp, _ in results]
    data = [round((count / total) * 100) for _, count in results]
    raw = [count for _, count in results]
    return jsonify({"labels": labels, "data": data, "raw": raw})

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe("arduino/cockroaches")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"MQTT message received: {payload}")
    if ', ' in payload:
        timestamp, message = payload.split(', ', 1)
    else:
        timestamp, message = '', payload
    minute = timestamp[:16]
    temp = get_current_temperature()
    with app.app_context():
        detection = Detection(timestamp=timestamp, minute=minute, weather=temp)
        db.session.add(detection)
        db.session.commit()
    print(f"Emitting to socket: timestamp={timestamp}, message={message}, temp={temp}")
    socketio.emit('mqtt_message', {'timestamp': timestamp, 'message': message, 'temp': temp})

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed to topic!")

mqtt_client = mqtt.Client(client_id="cockroach_subscriber", callback_api_version=CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_subscribe = on_subscribe
mqtt_client.connect("broker.hivemq.com", 1883, 60)
mqtt_client.loop_start()

OPENWEATHER_API_KEY = "" #API KEY

def get_current_temperature():
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Corfu&APPID={OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        return data['main']['temp']
    except Exception as e:
        print(f"Weather API error: {e}")
        return None

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000)
