import sqlite3
import os
from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = 'rfid_data.db'

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rfid_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            badge_id TEXT NOT NULL,
            flemme NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT NOT NULL,
            nom_perso TEXT,
            vigueur INTEGER,
            agilite INTEGER,
            intelligence INTEGER,
            ruse INTEGER,
            volonte INTEGER,
            presence INTEGER,
            recherche BOOL,
            en_fuite BOOL,
            RAS BOOL,
            endette BOOL,
            malfrat BOOL,
            credits INTEGER
        )
    ''')
    conn.commit()
    
    cursor.execute('SELECT COUNT(*) FROM rfid_log')
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute('''INSERT INTO rfid_log 
            (badge_id, file_path, nom_perso, recherche, en_fuite, RAS, endette, malfrat, vigueur, agilite, intelligence, ruse, volonte, presence, credits) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            ('demo123', 'model.stl', 'Personnage Demo', 0, 0, 1, 0, 0, 8, 7, 6, 5, 9, 4, 1500))
        conn.commit()
    
    conn.close()

badge_id = "demo123"

@app.route('/api/data')
def get_data():
    global badge_id
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM rfid_log WHERE badge_id = ?', (badge_id,))
        existing_data = cursor.fetchone()
        
        if not existing_data:
            return jsonify({"error": "No data found"}), 404
        
        bool_column_names = ["recherche", "en_fuite", "RAS", "endette", "malfrat"]
        situation = next(
            (column_name for column_name, value in zip(bool_column_names, existing_data[12:17]) if value == 1),
            "None"
        )
        if situation == "recherche":
            situation = "Recherché"
        elif situation == "en_fuite":
            situation = "En fuite"
        elif situation == "RAS":
            situation = "Rien à signaler"
        elif situation == "endette":
            situation = "Endetté"
        elif situation == "malfrat":
            situation = "Malfrat"

        data = {
            "file_path": existing_data[4],
            "nom_perso": existing_data[5],
            "vigueur": existing_data[6],
            "presence": existing_data[11],
            "agilite": existing_data[7],
            "intelligence": existing_data[8],
            "volonte": existing_data[10],
            "ruse": existing_data[9],
            "credit": existing_data[17],
            "situation": situation
        }
        return jsonify(data)

@app.route('/')
def serve_frontend():
    return send_file('Frontend.html')

@app.route('/three.js-dev/<path:filename>')
def serve_threejs(filename):
    return send_from_directory('three.js-dev', filename)

@app.route('/3D/<path:filename>')
def serve_3d_models(filename):
    return send_from_directory('3D', filename)

if __name__ == '__main__':
    init_database()
    app.run(host='0.0.0.0', port=5000, debug=False)
