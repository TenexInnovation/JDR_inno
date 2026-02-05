# JDR Badge Manager

**Gestionnaire de badges RFID pour jeux de rôle sur table**

Une application de bureau moderne pour gérer les personnages de vos parties de JDR via des badges RFID. Affichez les statistiques, la situation et visualisez les modèles 3D de vos personnages en un scan !

---

## Aperçu

L'application se compose de deux interfaces :

- **Interface Admin** : Créez, modifiez et supprimez des personnages avec leurs statistiques complètes
- **Interface Utilisateur** : Visualisez les informations d'un personnage en scannant son badge (ou en simulation)

### Statistiques disponibles
| Stat | Description |
|------|-------------|
| Vigueur | Force physique et endurance |
| Agilité | Rapidité et dextérité |
| Intelligence | Capacités mentales et connaissances |
| Ruse | Astuce et capacité de manipulation |
| Volonté | Détermination et résistance mentale |
| Présence | Charisme et influence sociale |

### Situations
- **RAS** (Rien à signaler) - Vert
- **Recherché** - Rouge
- **En fuite** - Orange
- **Endetté** - Jaune
- **Malfrat** - Violet

---

## Technologies utilisées

| Technologie | Utilisation |
|-------------|-------------|
| Python 3.11+ | Langage principal |
| PyQt5 | Interface graphique desktop |
| SQLite | Base de données locale |
| VTK | Rendu 3D des modèles STL |
| PySerial | Communication Arduino |

---

## Installation

### Prérequis
- Python 3.11 ou supérieur
- pip (gestionnaire de paquets Python)

### Windows

```powershell
# Cloner le projet
git clone https://github.com/TenexInnovation/JDR_inno.git
cd JDR_inno

# Créer un environnement virtuel (recommandé)
python -m venv venv
.\venv\Scripts\activate

# Installer les dépendances
pip install PyQt5 vtk pyserial
```

### Linux (Ubuntu/Debian)

```bash
# Cloner le projet
git clone https://github.com/TenexInnovation/JDR_inno.git
cd JDR_inno

# Créer un environnement virtuel (recommandé)
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances système pour Qt
sudo apt-get install python3-pyqt5 libxcb-xinerama0

# Installer les dépendances Python
pip install PyQt5 vtk pyserial
```

### Linux (Arch/Manjaro)

```bash
# Dépendances système
sudo pacman -S python-pyqt5

# Dépendances Python
pip install vtk pyserial
```

---

## Lancer l'application

```bash
# Windows
python main.py

# Linux
python3 main.py
```

L'application s'ouvrira avec la fenêtre principale contenant :
- Bouton pour ouvrir l'interface Admin
- Bouton pour ouvrir l'interface Utilisateur
- Section Arduino : sélection du port COM, connexion/déconnexion
- Champ de simulation de badge (pour tester sans Arduino)

---

## Ajouter des données de test

Pour créer des personnages de test, exécutez ce script Python :

```python
# Fichier: add_test_data.py
from app.database import add_character, init_database

init_database()

# Zara Vex - Rusée et riche, situation normale
add_character('BADGE001', '', 'Zara Vex', 8, 6, 4, 9, 5, 7, 2500, 'RAS')

# Marcus Dorn - Fort et volontaire, Recherché
add_character('BADGE002', '', 'Marcus Dorn', 9, 3, 7, 4, 8, 6, 150, 'recherche')

# Lyra Shade - Agile et intelligente, En fuite
add_character('BADGE003', '', 'Lyra Shade', 3, 9, 8, 7, 4, 5, -500, 'en_fuite')

print("3 personnages de test ajoutés!")
```

Puis lancez :
```bash
python add_test_data.py
```

---

## Fichiers 3D

### Où placer les modèles 3D

Les modèles 3D doivent être au format **STL** et placés dans le dossier `3D/` à la racine du projet :

```
JDR_inno/
├── 3D/
│   ├── zara_vex.stl
│   ├── marcus_dorn.stl
│   └── lyra_shade.stl
├── app/
├── main.py
└── ...
```

### Lier un modèle 3D à un personnage

1. Ouvrez l'**Interface Admin**
2. Sélectionnez le personnage dans la liste (ou créez-en un nouveau)
3. Dans le champ **"Chemin modèle 3D"**, entrez le chemin relatif vers le fichier STL :
   ```
   3D/nom_du_modele.stl
   ```
4. Cliquez sur **"Modifier"** (ou "Ajouter" pour un nouveau personnage)

Le modèle 3D sera affiché dans l'Interface Utilisateur lors du scan du badge correspondant.

### Formats supportés
- `.stl` (STereoLithography) - Format recommandé

---

## Structure du projet

```
JDR_inno/
├── main.py                  # Point d'entrée - Fenêtre principale avec support Arduino
├── app/
│   ├── __init__.py          # Module Python
│   ├── database.py          # Gestion SQLite (CRUD personnages)
│   ├── admin_window.py      # Interface d'administration
│   └── user_window.py       # Interface utilisateur (affichage + rendu 3D VTK)
├── 3D/                      # Dossier pour les modèles 3D STL
├── rfid_data.db             # Base de données SQLite (créée automatiquement)
├── Code arduino jdr.txt     # Code Arduino pour le lecteur RFID RC522
├── README.md                # Documentation
└── replit.md                # Configuration Replit
```

---

## Utilisation avec Arduino (optionnel)

L'application supporte nativement la connexion à un lecteur RFID Arduino.

**Matériel requis :**
- Arduino Uno/Nano
- Module RFID RC522
- Badges/cartes RFID

**Configuration :**

1. Uploadez le code depuis `Code arduino jdr.txt` sur votre Arduino via l'IDE Arduino
2. Connectez l'Arduino à votre PC
3. Dans l'application, sélectionnez le port COM dans la liste déroulante
4. Cliquez sur "Connecter"
5. Scannez un badge - l'ID s'affiche automatiquement dans l'interface utilisateur

**Câblage RC522 → Arduino Uno :**
| RC522 | Arduino |
|-------|---------|
| SDA   | Pin 10  |
| SCK   | Pin 13  |
| MOSI  | Pin 11  |
| MISO  | Pin 12  |
| GND   | GND     |
| RST   | Pin 9   |
| 3.3V  | 3.3V    |

**Mode simulation :** Si vous n'avez pas d'Arduino, utilisez le champ "Simulation" pour entrer manuellement les IDs de badge (ex: BADGE001, BADGE002, BADGE003)

---

## Licence

Projet développé pour TenexInnovation.

---

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.
