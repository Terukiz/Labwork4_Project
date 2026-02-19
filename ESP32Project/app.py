import serial
import threading
import time
from flask import Flask, render_template
from flask_socketio import SocketIO

SERIAL_PORT = "/dev/ttyUSB0"  # change if needed
BAUDRATE = 9600

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ✅ Alert hold variables
last_alert = None
last_alert_time = 0
ALERT_HOLD_TIME = 2  # seconds


def read_serial_port():
    global last_alert, last_alert_time

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

                            # 🔍 Voltage checking
                            if voltage is not None:
                                if voltage < 2:
                                    alert_message = f"⚠️ WARNING: Voltage is below 2V (Current: {voltage}V)"
                                elif voltage > 3:
                                    alert_message = f"⚠️ WARNING: Voltage exceeds 3V (Current: {voltage}V)"
                                elif voltage >= 3.3:
                                    alert_message = f"⚠️ WARNING: Voltage exceeds 3.3V (Current: {voltage}V)"

                            current_time = time.time()

                            # ✅ Keep alert for at least 2 seconds
                            if alert_message:
                                if (last_alert != alert_message) and (current_time - last_alert_time < ALERT_HOLD_TIME):
                                    pass  # Ignore new alert during hold time
                                else:
                                    last_alert = alert_message
                                    last_alert_time = current_time
                                    socketio.emit("voltage_alert", {"message": alert_message})
                                    print(alert_message)

                            # Send normal serial data
                            socketio.emit(
                                "serial_data",
                                {
                                    "led": data_list[0],
                                    "voltage": data_list[1],
                                    "touch": data_list[2],
                                }
                            )

                time.sleep(0.01)

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
    socketio.run(app, host="0.0.0.0", port=6767, debug=False, allow_unsafe_werkzeug=True)