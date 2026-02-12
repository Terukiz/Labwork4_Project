import serial
import threading
import time
from flask import Flask, render_template
from flask_socketio import SocketIO

SERIAL_PORT = "/dev/ttyUSB0"  # Double check this is correct (ls /dev/tty*)
BAUDRATE = 9600

app = Flask(__name__)
# Added async_mode and logger for better debugging
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

def read_serial_port():
    while True:
        ser = None
        try:
            # Added dsrdtr=True which helps some ESP32 boards maintain connection
            ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
            print("✅ Connected to ESP32 Serial")

            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode("utf-8", errors="ignore").strip()

                    if line:
                        print(f"RAW Data: {line}") # Verify this prints in your terminal
                        data_list = [item.strip() for item in line.split(",")]

                        if len(data_list) >= 3:
                            # Emit using the socketio instance directly
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
    # Start thread
    thread = threading.Thread(target=read_serial_port, daemon=True)
    thread.start()
    # Use allow_unsafe_werkzeug if not using eventlet
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, allow_unsafe_werkzeug=True)