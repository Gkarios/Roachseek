# RoachSeek MQTT Web Visualizer

This project is a web application that visualizes payload data received from an MQTT topic. It uses Flask as the web framework and Paho MQTT for subscribing to the MQTT topic.

## Project Structure

```
mqtt-web-visualizer
├── app.py                # Main application file
├── requirements.txt      # Project dependencies
├── static
│   └── style.css         # CSS styles for the web application
├── templates
│   └── index.html        # HTML template for displaying data
├── Arduino
│   └── mic.py            # For publicizing to a HiveMQ topic
│   └── microphone.ino    # Microphone Setup for an Ardino Uno + Electret digital microphone
│
└── README.md             # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone https://github.com/Gkarios/Roachseek.git
   cd Roachseek
   ```

2. **Install dependencies:**
   It is recommended to use a virtual environment. You can create one using:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
   Then install the required packages:
   ```
   pip install -r requirements.txt

   ``
   To fetch local weather, you need an OpenWeatherMap API key. Inside app.py use it on the empty OPENWEATHER_API_KEY variable and change the location of the q=_ field to your local city
   
   ``

3. **Run the application:**
   ```
   python app.py
   ```
   The application will start a web server, and you can access it at `http://127.0.0.1:5000`.

## Usage

Once the application is running, it will subscribe to an MQTT topic. Any messages published to this topic will be displayed on the web page along with their timestamps and corresponding weather.
