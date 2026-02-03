# JDR Badge Manager

## Overview
This is an RFID badge management system for tabletop RPG games. It displays character information with 3D model visualization using Three.js.

## Project Structure
- `server.py` - Flask backend that serves the frontend and API
- `Frontend.html` - Main frontend with Three.js 3D viewer and character stats display
- `admin-interface.py` - Original desktop admin interface (requires Tkinter and Arduino - not compatible with Replit cloud environment)
- `three.js-dev/` - Three.js library for 3D rendering
- `3D/` - Directory for STL 3D models

## Running the Project
The Flask server runs on port 5000 and serves:
- `/` - The main frontend HTML
- `/api/data` - JSON API for character data
- `/three.js-dev/*` - Three.js library files
- `/3D/*` - 3D model files (STL format)

## Database
Uses SQLite (`rfid_data.db`) to store character information including:
- Badge ID
- Character name
- Stats (Vigueur, Agilite, Intelligence, Ruse, Volonte, Presence)
- Credits
- Situation status

## Notes
- The original admin-interface.py uses Tkinter GUI and Arduino serial communication which are not available in Replit's cloud environment
- A demo character is automatically created in the database for testing
- To add STL 3D models, place them in the `3D/` directory

## Recent Changes
- 2026-02-03: Adapted project for Replit environment with Flask-based server
