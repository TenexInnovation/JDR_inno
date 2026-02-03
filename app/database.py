import sqlite3
import os

DB_PATH = 'rfid_data.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rfid_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            badge_id TEXT NOT NULL UNIQUE,
            flemme NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT DEFAULT '',
            nom_perso TEXT,
            vigueur INTEGER DEFAULT 5,
            agilite INTEGER DEFAULT 5,
            intelligence INTEGER DEFAULT 5,
            ruse INTEGER DEFAULT 5,
            volonte INTEGER DEFAULT 5,
            presence INTEGER DEFAULT 5,
            recherche BOOL DEFAULT 0,
            en_fuite BOOL DEFAULT 0,
            RAS BOOL DEFAULT 1,
            endette BOOL DEFAULT 0,
            malfrat BOOL DEFAULT 0,
            credits INTEGER DEFAULT 100
        )
    ''')
    conn.commit()
    conn.close()

def get_all_characters():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM rfid_log ORDER BY nom_perso')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_character_by_badge(badge_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM rfid_log WHERE badge_id = ?', (badge_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def add_character(badge_id, file_path, nom_perso, vigueur, agilite, intelligence, 
                  ruse, volonte, presence, credits, situation):
    conn = get_connection()
    cursor = conn.cursor()
    
    bool_values = get_situation_bools(situation)
    
    cursor.execute('''INSERT INTO rfid_log 
        (badge_id, file_path, nom_perso, vigueur, agilite, intelligence, ruse, volonte, presence, credits,
         recherche, en_fuite, RAS, endette, malfrat) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (badge_id, file_path, nom_perso, vigueur, agilite, intelligence, ruse, volonte, presence, credits,
         *bool_values))
    conn.commit()
    conn.close()

def update_character(badge_id, file_path, nom_perso, vigueur, agilite, intelligence,
                     ruse, volonte, presence, credits, situation):
    conn = get_connection()
    cursor = conn.cursor()
    
    bool_values = get_situation_bools(situation)
    
    cursor.execute('''
        UPDATE rfid_log SET 
        file_path = ?, nom_perso = ?, vigueur = ?, agilite = ?, intelligence = ?,
        ruse = ?, volonte = ?, presence = ?, credits = ?,
        recherche = ?, en_fuite = ?, RAS = ?, endette = ?, malfrat = ?
        WHERE badge_id = ?
    ''', (file_path, nom_perso, vigueur, agilite, intelligence, ruse, volonte, presence, credits,
          *bool_values, badge_id))
    conn.commit()
    conn.close()

def delete_character(badge_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rfid_log WHERE badge_id = ?", (badge_id,))
    conn.commit()
    conn.close()

def get_situation_bools(situation):
    situations = ["recherche", "en_fuite", "RAS", "endette", "malfrat"]
    return [1 if s == situation else 0 for s in situations]

def get_situation_from_row(row):
    if row is None:
        return "RAS"
    bool_column_names = ["recherche", "en_fuite", "RAS", "endette", "malfrat"]
    for i, name in enumerate(bool_column_names):
        if row[12 + i] == 1:
            return name
    return "RAS"

def get_situation_display(situation):
    mapping = {
        "recherche": "Recherché",
        "en_fuite": "En fuite",
        "RAS": "Rien à signaler",
        "endette": "Endetté",
        "malfrat": "Malfrat"
    }
    return mapping.get(situation, "Rien à signaler")
