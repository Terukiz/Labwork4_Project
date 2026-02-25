import serial
import threading
import time
import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO

SERIAL_PORT = "/dev/cu.usbserial-0001" 
BAUDRATE = 9600

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

ser = None 
user_sessions = {}

def read_serial_port():
    global ser
    while True:
        try:
            if ser is None or not ser.is_open:
                ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
                print(f"Connected to {SERIAL_PORT}")

            while ser.is_open:
                if ser.in_waiting > 0:
                    line = ser.readline().decode("utf-8", errors="ignore").strip()
                    if not line: continue
                    
                    print(f"Serial In: {line}")

                    if line.startswith("RFID:"):
                        uid = line.split(":")[1].strip()
                        now = datetime.datetime.now()
                        if uid not in user_sessions:
                            user_sessions[uid] = now
                            socketio.emit("rfid_event", {"text": f"ID: {uid} Entered", "color": "#4ade80"})
                        else:
                            start_time = user_sessions.pop(uid)
                            total_sec = int((now - start_time).total_seconds())
                            
                            if total_sec > 900: analysis, color = "Scrolling Reels 📱", "#f87171"
                            elif total_sec > 300: analysis, color = "Long Session 💩🔥", "#fb923c"
                            elif total_sec > 60: analysis, color = "Heavy usage 💩", "#facc15"
                            else: analysis, color = "Quick visit", "#38bdf8"
                                
                            socketio.emit("rfid_event", {"text": f"ID: {uid} | {total_sec}s | {analysis}", "color": color})

                    elif line.startswith("DATA:"):
                        try:
                            content = line.split(":")[1]
                            d = content.split(",")
                            if len(d) >= 3:
                                socketio.emit("serial_data", {
                                    "led": d[0].strip(),
                                    "voltage": d[1].strip(),
                                    "touch": d[2].strip()
                                })
                        except: pass
                time.sleep(0.01)
        except:
            ser = None
            time.sleep(2)

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("toggle_led")
def handle_toggle():
    global ser
    if ser and ser.is_open: ser.write(b'T') 

if __name__ == "__main__":
    thread = threading.Thread(target=read_serial_port, daemon=True)
    thread.start()
    socketio.run(app, host="127.0.0.1", port=6767, debug=False)