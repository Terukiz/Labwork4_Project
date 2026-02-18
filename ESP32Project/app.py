import serial
import threading
import time
from flask import Flask, render_template
from flask_socketio import SocketIO

SERIAL_PORT = "/dev/ttyUSB0" #change to "COM3" (work on window) if it have any problem in the future
BAUDRATE = 9600

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

def read_serial_port():
    while True:
        ser = None
        try:
            ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
            print("✅ Connected to ESP32 Serial")

            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode("utf-8", errors="ignore").strip()

                    if line:
                        print(f"RAW Data: {line}")
                        data_list = [item.strip() for item in line.split(",")]

                        if len(data_list) >= 3:
                            try:
                                voltage = float(data_list[1])
                            except ValueError:
                                voltage = None
                            
                            alert_message = None
                            if voltage is not None:
                                if voltage < 0:
                                    alert_message = f"⚠️ WARNING: Voltage is below 0V (Current: {voltage}V)"
                                elif voltage > 3.6:
                                    alert_message = f"🔴 CRITICAL: Voltage exceeds 3.6V (Current: {voltage}V)"
                                elif voltage > 3.3:
                                    alert_message = f"🟡 WARNING: Voltage exceeds 3.3V (Current: {voltage}V)"
                            
                            if alert_message:
                                socketio.emit("voltage_alert", {"message": alert_message})
                                print(alert_message)
                            
                            socketio.emit(
                                "serial_data",
                                {
                                    "led": data_list[0],
                                    "voltage": data_list[1],
                                    "touch": data_list[2],
                                }
                            )
                time.sleep(0.01) # Faster polling

        except (serial.SerialException, OSError) as e:
            print(f"❌ Serial error: {e}")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            time.sleep(2)
        finally:
            if ser and ser.is_open:
                ser.close()

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    thread = threading.Thread(target=read_serial_port, daemon=True)
    thread.start()
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, allow_unsafe_werkzeug=True)
