import tkinter as tk
import serial
import sqlite3
import os
from PIL import Image, ImageTk
import numpy as np
from stl import mesh
import vtk
from vtk import vtkSTLReader, vtkPolyDataMapper, vtkActor, vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor, vtkInteractorStyleTrackballCamera
from threading import Thread
from flask import Flask, jsonify
from flask_cors import CORS
import webbrowser
from tkinter import ttk
import webview  # type: ignore


# commande à saisir dans le CMD pour lancer le serveur local :
# python3 -m http.server




# Initialize the database connection
conn = sqlite3.connect('rfid_data.db')
cursor = conn.cursor()

# Create a table if it doesn't exist
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

# Open the serial connection
arduino_port = "COM5"  # Change to your actual port
baud_rate = 9600
ser = serial.Serial(arduino_port, baud_rate, timeout=1)

# Variable to keep track of the last badge ID
last_badge_id = ""

# Variable to store the 3D file access path
access_path = "../3D/"
file_name = ""

badge_id = ""

def ui():
    app = Flask(__name__)
    CORS(app)

    @app.route('/api/data')
    def get_data():
        global badge_id
        print(badge_id)
        with sqlite3.connect('rfid_data.db') as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM rfid_log WHERE badge_id = ?', (badge_id,))
            existing_data = cursor.fetchone()
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

    class ServerThread(Thread):
        def run(self):
            app.run(host='0.0.0.0', port=5000, use_reloader=False)


    server_thread = ServerThread()
    server_thread.daemon = True
    server_thread.start()
    webbrowser.open('http://localhost:8000/Desktop/Frontend.html')

def read_badge():
    global last_badge_id, badge_id
    try:
        while ser.in_waiting > 0:
            badge_id = ser.readline().decode('utf-8').strip()
            if badge_id:
                last_badge_id = badge_id
                badge_id_entry.config(state="normal")
                badge_id_entry.delete(0, tk.END)
                badge_id_entry.insert(tk.END, badge_id)
                badge_id_entry.config(state="readonly")
                cursor.execute("SELECT * FROM rfid_log WHERE badge_id=?", (badge_id,))
                existing_data = cursor.fetchone()
                if not existing_data:
                    last_badge_nodb.config(text="Ce badge n'est pas dans la Base de Données.")
                    vigueur_entry.delete(0, tk.END)
                    presence_entry.delete(0, tk.END)
                    agilite_entry.delete(0, tk.END)
                    intelligence_entry.delete(0, tk.END)
                    volonte_entry.delete(0, tk.END)
                    ruse_entry.delete(0, tk.END)
                    credit_entry.delete(0, tk.END)
                    bool_dropdown.set("")
                    nom_perso_entry.delete(0, tk.END)
                    path_entry.delete(0, tk.END)
                else:
                    last_badge_nodb.config(text=f"")
                    ui()
                    # put the character's stats in the entry fields
                    vigueur_entry.delete(0, tk.END)
                    vigueur_entry.insert(tk.END, existing_data[6])
                    presence_entry.delete(0, tk.END)
                    presence_entry.insert(tk.END, existing_data[11])
                    agilite_entry.delete(0, tk.END)
                    agilite_entry.insert(tk.END, existing_data[7])
                    intelligence_entry.delete(0, tk.END)
                    intelligence_entry.insert(tk.END, existing_data[8])
                    volonte_entry.delete(0, tk.END)
                    volonte_entry.insert(tk.END, existing_data[10])
                    ruse_entry.delete(0, tk.END)
                    ruse_entry.insert(tk.END, existing_data[9])
                    credit_entry.delete(0, tk.END)
                    credit_entry.insert(tk.END, existing_data[17])
                    # situtation, nom_perso et file_path
                    bool_column_names = ["recherche", "en_fuite", "RAS", "endette", "malfrat"]
                    situation = next(
                        (column_name for column_name, value in zip(bool_column_names, existing_data[12:17]) if value == 1),
                        "None"
                    )
                        
                    bool_dropdown.set(situation)
                    nom_perso_entry.delete(0, tk.END)
                    nom_perso_entry.insert(tk.END, existing_data[5])
                    path_entry.delete(0, tk.END)
                    path_entry.insert(tk.END, existing_data[4])
                    
    except Exception as e:
        print("Erreur lors de la lecture du bagde : ", e)
    root.after(1000, read_badge)

def add_badge():
    if last_badge_id:
        cursor.execute("SELECT * FROM rfid_log WHERE badge_id=?", (last_badge_id,))
        existing_data = cursor.fetchone()
        if not existing_data:
            file_name = path_entry.get()
            nom_perso = nom_perso_entry.get()
            selected_bool = bool_var.get()

            # Integer values
            try:
                vigueur = int(vigueur_entry.get())
                agilite = int(agilite_entry.get())
                intelligence = int(intelligence_entry.get())
                ruse = int(ruse_entry.get())
                volonte = int(volonte_entry.get())
                presence = int(presence_entry.get())
                credit = int(credit_entry.get())
            except ValueError:
                last_badge_nodb.config(text="Les champs d'entiers doivent contenir des valeurs numériques entières.")
                return

            if file_name and nom_perso:
                # Determine which BOOL field is true
                bool_values = [0] * 5
                bool_values[bool_options.index(selected_bool)] = 1
                cursor.execute('''INSERT INTO rfid_log 
                    (badge_id, file_path, nom_perso, recherche, en_fuite, RAS, endette, malfrat, vigueur, agilite, intelligence, ruse, volonte, presence, credits) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (last_badge_id, file_name, nom_perso, *bool_values, vigueur, agilite, intelligence, ruse, volonte, presence, credit))
                conn.commit()
                last_badge_nodb.config(text="Badge ajouté à la Base de Données.")
                ui()
            else:
                last_badge_nodb.config(text="Le nom du badge, le chemin du fichier et le nom du personnage ne peuvent pas être nuls.")
        else:
            last_badge_nodb.config(text="Ce badge est déjà dans la Base de Données.")
    else:
        last_badge_nodb.config(text="Aucun badge détecté.")


def update_badge():
    if last_badge_id:
        cursor.execute("SELECT * FROM rfid_log WHERE badge_id=?", (last_badge_id,))
        existing_data = cursor.fetchone()
        if existing_data: 
            file_name = path_entry.get()
            nom_perso = nom_perso_entry.get()
            selected_bool = bool_var.get()

            # Integer values
            try:
                vigueur = int(vigueur_entry.get())
                agilite = int(agilite_entry.get())
                intelligence = int(intelligence_entry.get())
                ruse = int(ruse_entry.get())
                volonte = int(volonte_entry.get())
                presence = int(presence_entry.get())
                credit = int(credit_entry.get())
            except ValueError:
                last_badge_nodb.config(text="Les champs d'entiers doivent contenir des valeurs numériques entières.")
                return

            if file_name and nom_perso:
                bool_values = [0] * 5
                bool_values[bool_options.index(selected_bool)] = 1
                cursor.execute('''
                    UPDATE rfid_log SET 
                    file_path = ?, nom_perso = ?, 
                    recherche = ?, en_fuite = ?, RAS = ?, endette = ?, malfrat = ?, 
                    vigueur = ?, agilite = ?, intelligence = ?, ruse = ?, volonte = ?, presence = ?, credits = ?
                    WHERE badge_id = ?
                ''', (file_name, nom_perso, *bool_values, vigueur, agilite, intelligence, ruse, volonte, presence, credit, last_badge_id))

                conn.commit()
                last_badge_nodb.config(text="Badge mis à jour dans la Base de Données.")
                ui()
            else:
                last_badge_nodb.config(text="Le nom du badge, le chemin du fichier et le nom du personnage ne peuvent pas être nuls.")
        else:
            last_badge_nodb.config(text="Ce badge n'est pas dans la Base de Données.")
    else:
        last_badge_nodb.config(text="Aucun badge détecté.")

def delete_badge():
    if last_badge_id:
        # Fetch name associated with badge_id from the database
        cursor.execute("SELECT * FROM rfid_log WHERE badge_id=?", (last_badge_id,))
        existing_data = cursor.fetchone()
        if existing_data:
            cursor.execute("DELETE FROM rfid_log WHERE badge_id=?", (last_badge_id,))
            conn.commit()
            last_badge_nodb.config(text="Badge supprimé de la Base de Données.")
        else:
            last_badge_nodb.config(text="Ce badge n'est pas dans la Base de Données.")
    else:
        last_badge_nodb.config(text="Aucun badge détecté.")


# Create the main window
root = tk.Tk()
root.title("Badge Manager")
root.geometry("600x400")

path_label = tk.Label(root, text="Nom du fichier :")
path_label.pack(pady=5)
path_entry = tk.Entry(root)
path_entry.pack(pady=5)

nom_perso_label = tk.Label(root, text="Nom du Personnage :")
nom_perso_label.pack(pady=5)
nom_perso_entry = tk.Entry(root)
nom_perso_entry.pack(pady=5)

# Dropdown for BOOL values
bool_label = tk.Label(root, text="Situation :")
bool_label.pack(pady=5)
bool_var = tk.StringVar()
bool_options = ["recherche", "en_fuite", "RAS", "endette", "malfrat"]
bool_dropdown = ttk.Combobox(root, textvariable=bool_var, values=bool_options)
bool_dropdown.set("")  # set default value
bool_dropdown.pack(pady=5)

# Integer fields
def create_integer_field(label_text):
    label = tk.Label(root, text=label_text)
    label.pack(pady=5)
    entry = tk.Entry(root)
    entry.pack(pady=5)
    return entry

vigueur_entry = create_integer_field("Vigueur :")
agilite_entry = create_integer_field("Agilite :")
intelligence_entry = create_integer_field("Intelligence :")
ruse_entry = create_integer_field("Ruse :")
volonte_entry = create_integer_field("Volonte :")
presence_entry = create_integer_field("Presence :")
credit_entry = create_integer_field("Credits :")

# Add buttons to the main window
add_badge_button = tk.Button(root, text="Ajouter un badge", command=add_badge)
add_badge_button.pack(pady=10)

update_badge_button = tk.Button(root, text="Modifer le badge", command=update_badge)
update_badge_button.pack(pady=10)

delete_badge_button = tk.Button(root, text="Supprimer un badge", command=delete_badge)
delete_badge_button.pack(pady=10)

# Create Entry widgets for badge ID and name
last_badge_label = tk.Label(root, text="Dernier badge détecté :")
last_badge_label.pack()

badge_id_entry = tk.Entry(root, state="readonly")
badge_id_entry.pack()

last_badge_nodb = tk.Label(root, text="")
last_badge_nodb.pack()

# Start badge reading
read_badge()

# Run the application
root.mainloop()

# Cleanup
ser.close()
conn.close()