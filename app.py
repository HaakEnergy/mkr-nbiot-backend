from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "data.db"

# Datenbank initialisieren
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device TEXT,
            timestamp TEXT,
            signal INTEGER,
            temperature REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Standardroute
@app.route("/")
def index():
    return "NB-IoT Railway Backend läuft."

# POST-Daten empfangen
@app.route("/api/data", methods=["POST"])
def receive_data():
    data = request.get_json(force=True)
    print("Empfangen:", data)

    if not data:
        return jsonify({"error": "no data"}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO measurements (device, timestamp, signal, temperature) VALUES (?, ?, ?, ?)", (
        data.get("device"),
        data.get("timestamp"),
        int(data.get("signal", 0)),
        float(data.get("temperature", 0.0))
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 200

# Daten abfragen
@app.route("/api/data", methods=["GET"])
def get_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM measurements ORDER BY id DESC LIMIT 100")
    rows = c.fetchall()
    conn.close()
    return jsonify([
        {"id": r[0], "device": r[1], "timestamp": r[2], "signal": r[3], "temperature": r[4]}
        for r in rows
    ])

# WICHTIG: Start erst ganz am Ende
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 80)))
