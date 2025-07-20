from flask import Flask, request, jsonify
import sqlite3, os
from datetime import datetime

DB = 'data.db'
app = Flask(__name__)

def init_db():
    if not os.path.isfile(DB):
        conn = sqlite3.connect(DB)
        conn.execute('''CREATE TABLE sensor_data (
            device TEXT, timestamp TEXT,
            signal INTEGER, temperature REAL
        )''')
        conn.close()

@app.route('/api/data', methods=['POST'])
def receive():
    data = request.get_json()
    conn = sqlite3.connect(DB)
    conn.execute(
        'INSERT INTO sensor_data (device, timestamp, signal, temperature) VALUES (?, ?, ?, ?)',
        (data['device'], data['timestamp'], data['signal'], data['temperature'])
    )
    conn.commit()
    conn.close()
    return jsonify({"status":"ok"})

def receive_data():
    try:
        data = request.get_json(force=True)
        print("Empfangen:", data)

        if not data:
            return jsonify({"error": "no data received"}), 400

        with open("data.txt", "a") as f:
            json.dump(data, f)
            f.write("\n")
        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("Fehler beim Verarbeiten:", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/data', methods=['GET'])
def send():
    device = request.args.get('device')
    conn = sqlite3.connect(DB)
    if device:
        rows = conn.execute('SELECT * FROM sensor_data WHERE device=? ORDER BY timestamp DESC LIMIT 100', (device,)).fetchall()
    else:
        rows = conn.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 100').fetchall()
    conn.close()
    return jsonify([{"device":r[0], "timestamp":r[1], "signal":r[2], "temperature":r[3]} for r in rows])

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
