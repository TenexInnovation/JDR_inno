# JDR Badge Manager

## Overview
Application de bureau complète pour la gestion de badges RFID dans les jeux de rôle sur table. Affiche les informations des personnages avec une interface moderne PyQt5.

## Project Structure
- `main.py` - Application principale avec fenêtre de lancement
- `app/` - Module de l'application
  - `database.py` - Gestion de la base de données SQLite
  - `admin_window.py` - Interface d'administration (gestion des personnages)
  - `user_window.py` - Interface utilisateur (affichage des personnages avec stats)
- `server.py` - Serveur Flask pour interface web (legacy)
- `Frontend.html` - Interface web avec Three.js (legacy)
- `admin-interface.py` - Interface admin originale Tkinter (legacy, nécessite Arduino)
- `3D/` - Répertoire pour les modèles 3D STL

## Architecture
### Fenêtre Principale
- Bouton pour ouvrir l'interface Admin
- Bouton pour ouvrir l'interface Utilisateur  
- Simulation de badge (pour tests sans Arduino)

### Interface Admin
- Liste des personnages enregistrés
- Formulaire de création/modification de personnage
- Statistiques: Vigueur, Agilité, Intelligence, Ruse, Volonté, Présence
- Gestion des situations: Recherché, En fuite, RAS, Endetté, Malfrat
- Crédits et chemin du modèle 3D

### Interface Utilisateur
- Affichage du nom du personnage en grand
- Bulles de statistiques colorées selon la valeur
- Visualisation 3D avec VTK (charge les fichiers STL avec rotation automatique)
- Affichage de la situation avec couleur dynamique
- Affichage des crédits

## Database
SQLite (`rfid_data.db`) avec les champs:
- badge_id, nom_perso, file_path
- vigueur, agilite, intelligence, ruse, volonte, presence
- credits, situation (recherche, en_fuite, RAS, endette, malfrat)

## Running the Project
L'application utilise PyQt5 et s'exécute via VNC dans Replit.
Commande: `xvfb-run -a python main.py`

## Technologies
- Python 3.11
- PyQt5 pour l'interface graphique
- SQLite pour la base de données
- VTK (disponible) pour le rendu 3D

## Recent Changes
- 2026-02-03: Implémentation du rendu 3D VTK avec rotation automatique des modèles STL
- 2026-02-03: Ajout du README.md complet avec instructions d'installation
- 2026-02-03: Ajout de personnages de test (BADGE001, BADGE002, BADGE003)
- 2026-02-03: Transformation en application de bureau complète avec PyQt5
- 2026-02-03: Création de l'interface admin avec gestion CRUD des personnages
- 2026-02-03: Création de l'interface utilisateur avec affichage des stats
- 2026-02-03: Simulation de badges pour les tests
