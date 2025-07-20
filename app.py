from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = "data.db"

# Init DB on startup
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

@app.route("/")
def index():
    return "NB-IoT Backend läuft."

@app.route("/api/data", methods=["POST"])
def receive_data():
    try:
        data = request.get_json(force=True)
        print("Empfangen:", data)

        if not data:
            return jsonify({"error": "no data received"}), 400

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO measurements (device, timestamp, signal, temperature) VALUES (?, ?, ?, ?)", (
            data.get("device"),
            data.get("timestamp"),
            int(data.get("signal")),
            float(data.get("temperature"))
        ))
        conn.commit()
        conn.close()

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("Fehler:", e)
        return jsonify({"error": str(e)}), 500

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
