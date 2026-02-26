# ESP32 RFID & Touch Sensor Monitoring System

A full-stack IoT project that combines an **ESP32 microcontroller** with a **Flask web application** to monitor RFID card interactions, LED control, touch sensor input, and voltage readings in real-time.

## 🌟 Features

- **RFID Card Detection**: Real-time monitoring of RFID card interactions using the MFRC522 reader
- **Session Tracking**: Automatic tracking of user sessions with duration analysis
- **Touch Sensor Input**: Capacitive touch sensor monitoring on ESP32
- **LED Control**: Remote LED toggling via web interface
- **Voltage Monitoring**: ADC voltage reading from the ESP32
- **Live Dashboard**: Real-time web dashboard with WebSocket communication
- **Activity Analysis**: Automatic categorization of user activity based on session duration

## 🏗️ Project Structure

```
├── app.py                 # Flask web server with SocketIO
├── platformio.ini         # PlatformIO configuration for ESP32
├── templates/
│   └── index.html         # Real-time dashboard UI
├── src/
│   └── led_touch.cpp      # ESP32 firmware (Arduino sketch)
├── include/               # Header files
├── lib/                   # Libraries
└── test/                  # Test files
```

## 🔧 Hardware Requirements

- **ESP32 Development Board**
- **MFRC522 RFID Reader Module**
- **LED** (with appropriate current-limiting resistor)
- **Capacitive Touch Sensor** (or use ESP32's built-in touch pins)
- **ADC Voltage Sensor**
- **USB Serial Cable** (for programming and serial communication)

## 📌 Pin Configuration

| Component | ESP32 Pin |
|-----------|-----------|
| RFID SS | GPIO 5 |
| RFID RST | GPIO 22 |
| RFID SCK | GPIO 18 |
| RFID MISO | GPIO 19 |
| RFID MOSI | GPIO 23 |
| LED | GPIO 27 |
| Touch Sensor | GPIO 14 |
| ADC | GPIO 34 |

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- PlatformIO CLI
- USB connection to ESP32

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Labwork4_Project
   ```

2. **Set up Python virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install flask flask-socketio python-socketio pyserial
   ```

4. **Build and upload ESP32 firmware**
   ```bash
   platformio run -e esp32dev -t upload
   ```
   > Update `SERIAL_PORT` in `app.py` to match your system (e.g., `/dev/ttyUSB0` on Linux, `COM3` on Windows)

5. **Run the Flask server**
   ```bash
   python app.py
   ```

6. **Access the dashboard**
   Open your browser and navigate to: `http://127.0.0.1:6767`

## 📡 Communication Protocol

### Serial Communication (ESP32 ↔ Python)

**ESP32 to Python:**
- `RFID:<UID>` - RFID card detected with unique ID
- `DATA:<LED_STATE>,<VOLTAGE>,<TOUCH_STATE>` - Sensor data stream

**Python to ESP32:**
- `T` - Toggle LED on/off

### WebSocket Events

**Server → Client:**
- `rfid_event` - RFID card detection and session analysis
- `serial_data` - Real-time sensor readings

**Client → Server:**
- `toggle_led` - Request LED state change

## 📊 Session Analysis Categories

Based on session duration, the system categorizes user activity:

| Duration | Category | Emoji |
|----------|----------|-------|
| > 900s (15 min) | Scrolling Reels | 📱 |
| > 300s (5 min) | Long Session | 💩🔥 |
| > 60s (1 min) | Heavy Usage | 💩 |
| ≤ 60s | Quick Visit | ✓ |

## 🖥️ Web Dashboard

The dashboard provides:
- Real-time RFID event feed with color-coded activity levels
- LED toggle button for remote control
- Live sensor data display (LED state, voltage, touch input)
- Activity timeline visualization
- Connection status indicator

## 🔌 Technologies Used

- **Backend**: Flask, Flask-SocketIO, PySerial
- **Frontend**: HTML5, CSS3, Chart.js, Socket.IO Client
- **Firmware**: Arduino Framework (PlatformIO)
- **Hardware**: ESP32, MFRC522 RFID Module

## ⚙️ Configuration

Edit `app.py` to customize:

```python
SERIAL_PORT = "/dev/cu.usbserial-0001"  # Update for your system
BAUDRATE = 9600                          # Must match ESP32 serial config
```

## 🐛 Troubleshooting

**Serial Port Connection Issues**
- Check USB cable connection
- List available ports: `python -m serial.tools.list_ports`
- Update `SERIAL_PORT` path in `app.py`

**RFID Module Not Detected**
- Verify SPI connections match pinout
- Confirm MFRC522 library is installed: `platformio lib list`
- Check power supply to RFID module (3.3V required)

**Dashboard Not Loading**
- Ensure Flask server is running
- Check firewall settings for port 6767
- Open browser console for WebSocket errors

## 📝 License

This project is provided as-is for educational purposes.

## 👤 Author

Labwork4 Project

---

For more information and updates, visit the repository.
