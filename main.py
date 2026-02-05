import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame, QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from app import database as db
from app.admin_window import AdminWindow
from app.user_window import UserWindow

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


class ArduinoReaderThread(QThread):
    badge_scanned = pyqtSignal(str)
    connection_status = pyqtSignal(bool, str)
    
    def __init__(self, port, baudrate=9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = False
        self.serial_connection = None
        
    def run(self):
        self.running = True
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            self.connection_status.emit(True, f"Connecté à {self.port}")
            
            while self.running:
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        self.badge_scanned.emit(line)
                        
        except Exception as e:
            self.connection_status.emit(False, f"Erreur: {str(e)}")
        finally:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
                
    def stop(self):
        self.running = False
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        self.wait()


class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("JDR Badge Manager")
        self.setGeometry(200, 200, 500, 450)
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; }
            QWidget { background-color: transparent; color: #ffffff; }
            QLabel { color: #ffffff; }
            QPushButton { 
                background-color: #2563eb; 
                color: white; 
                border: none; 
                padding: 15px 30px; 
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1d4ed8; }
            QPushButton#user { background-color: #16a34a; }
            QPushButton#user:hover { background-color: #15803d; }
            QPushButton#scan { background-color: #7c3aed; }
            QPushButton#scan:hover { background-color: #6d28d9; }
            QPushButton#connect { background-color: #dc2626; padding: 10px 20px; }
            QPushButton#connect:hover { background-color: #b91c1c; }
            QPushButton#connected { background-color: #16a34a; padding: 10px 20px; }
            QPushButton#connected:hover { background-color: #15803d; }
            QLineEdit { 
                background-color: #2a2a2a; 
                border: 1px solid #444; 
                border-radius: 5px; 
                padding: 10px;
                color: #ffffff;
            }
            QComboBox {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 8px;
                color: #ffffff;
            }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: none; }
            QFrame { background-color: #252525; border-radius: 10px; }
            QCheckBox { color: #888888; }
            QCheckBox::indicator { width: 18px; height: 18px; }
        """)
        
        db.init_database()
        
        self.admin_window = None
        self.user_window = None
        self.arduino_thread = None
        self.is_connected = False
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(15)
        
        title_label = QLabel("JDR Badge Manager")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Système de gestion de badges RFID")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #888888;")
        main_layout.addWidget(subtitle_label)
        
        main_layout.addSpacing(20)
        
        admin_btn = QPushButton("Ouvrir Interface Admin")
        admin_btn.clicked.connect(self.open_admin)
        main_layout.addWidget(admin_btn)
        
        user_btn = QPushButton("Ouvrir Interface Utilisateur")
        user_btn.setObjectName("user")
        user_btn.clicked.connect(self.open_user)
        main_layout.addWidget(user_btn)
        
        main_layout.addSpacing(10)
        
        arduino_frame = QFrame()
        arduino_layout = QVBoxLayout(arduino_frame)
        arduino_layout.setContentsMargins(15, 15, 15, 15)
        arduino_layout.setSpacing(10)
        
        arduino_title = QLabel("Lecteur RFID Arduino")
        arduino_title.setFont(QFont("Arial", 12, QFont.Bold))
        arduino_title.setStyleSheet("color: #ffffff;")
        arduino_layout.addWidget(arduino_title)
        
        port_layout = QHBoxLayout()
        
        port_label = QLabel("Port:")
        port_label.setStyleSheet("color: #888888;")
        port_layout.addWidget(port_label)
        
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(150)
        self.refresh_ports()
        port_layout.addWidget(self.port_combo)
        
        refresh_btn = QPushButton("↻")
        refresh_btn.setFixedWidth(40)
        refresh_btn.setStyleSheet("padding: 8px;")
        refresh_btn.clicked.connect(self.refresh_ports)
        port_layout.addWidget(refresh_btn)
        
        self.connect_btn = QPushButton("Connecter")
        self.connect_btn.setObjectName("connect")
        self.connect_btn.clicked.connect(self.toggle_arduino_connection)
        if not SERIAL_AVAILABLE:
            self.connect_btn.setEnabled(False)
            self.connect_btn.setText("pyserial manquant")
        port_layout.addWidget(self.connect_btn)
        
        arduino_layout.addLayout(port_layout)
        
        self.status_label = QLabel("Non connecté")
        self.status_label.setStyleSheet("color: #888888; font-size: 11px;")
        arduino_layout.addWidget(self.status_label)
        
        main_layout.addWidget(arduino_frame)
        
        main_layout.addSpacing(5)
        
        sim_frame = QFrame()
        sim_layout = QVBoxLayout(sim_frame)
        sim_layout.setContentsMargins(15, 15, 15, 15)
        sim_layout.setSpacing(10)
        
        sim_title = QLabel("Simulation (test sans Arduino)")
        sim_title.setFont(QFont("Arial", 12, QFont.Bold))
        sim_title.setStyleSheet("color: #ffffff;")
        sim_layout.addWidget(sim_title)
        
        badge_layout = QHBoxLayout()
        
        self.badge_entry = QLineEdit()
        self.badge_entry.setPlaceholderText("ID du badge (ex: BADGE001)...")
        self.badge_entry.returnPressed.connect(self.simulate_badge_scan)
        badge_layout.addWidget(self.badge_entry)
        
        scan_btn = QPushButton("Scanner")
        scan_btn.setObjectName("scan")
        scan_btn.clicked.connect(self.simulate_badge_scan)
        badge_layout.addWidget(scan_btn)
        
        sim_layout.addLayout(badge_layout)
        
        main_layout.addWidget(sim_frame)
        
        main_layout.addStretch()
        
    def refresh_ports(self):
        self.port_combo.clear()
        if SERIAL_AVAILABLE:
            ports = serial.tools.list_ports.comports()
            for port in ports:
                self.port_combo.addItem(f"{port.device} - {port.description}", port.device)
            if not ports:
                self.port_combo.addItem("Aucun port détecté", None)
        else:
            self.port_combo.addItem("pyserial non installé", None)
            
    def toggle_arduino_connection(self):
        if self.is_connected:
            self.disconnect_arduino()
        else:
            self.connect_arduino()
            
    def connect_arduino(self):
        port = self.port_combo.currentData()
        if not port:
            self.status_label.setText("Veuillez sélectionner un port valide")
            return
            
        self.arduino_thread = ArduinoReaderThread(port)
        self.arduino_thread.badge_scanned.connect(self.on_badge_scanned)
        self.arduino_thread.connection_status.connect(self.on_connection_status)
        self.arduino_thread.start()
        
    def disconnect_arduino(self):
        if self.arduino_thread:
            self.arduino_thread.stop()
            self.arduino_thread = None
        self.is_connected = False
        self.connect_btn.setText("Connecter")
        self.connect_btn.setObjectName("connect")
        self.connect_btn.setStyle(self.connect_btn.style())
        self.status_label.setText("Déconnecté")
        self.port_combo.setEnabled(True)
        
    def on_connection_status(self, connected, message):
        self.is_connected = connected
        self.status_label.setText(message)
        if connected:
            self.connect_btn.setText("Déconnecter")
            self.connect_btn.setObjectName("connected")
            self.port_combo.setEnabled(False)
        else:
            self.connect_btn.setText("Connecter")
            self.connect_btn.setObjectName("connect")
            self.port_combo.setEnabled(True)
        self.connect_btn.setStyle(self.connect_btn.style())
        
    def on_badge_scanned(self, badge_id):
        self.on_badge_selected(badge_id)
        
    def open_admin(self):
        if self.admin_window is None or not self.admin_window.isVisible():
            self.admin_window = AdminWindow(self)
            self.admin_window.badge_selected.connect(self.on_badge_selected)
            self.admin_window.show()
        else:
            self.admin_window.raise_()
            self.admin_window.activateWindow()
            
    def open_user(self):
        if self.user_window is None or not self.user_window.isVisible():
            self.user_window = UserWindow(self)
            self.user_window.show()
        else:
            self.user_window.raise_()
            self.user_window.activateWindow()
            
    def on_badge_selected(self, badge_id):
        self.open_user()
        if self.user_window:
            self.user_window.display_character(badge_id)
            self.user_window.raise_()
            self.user_window.activateWindow()
            
    def simulate_badge_scan(self):
        badge_id = self.badge_entry.text().strip()
        if badge_id:
            self.on_badge_selected(badge_id)
            
    def closeEvent(self, event):
        if self.arduino_thread:
            self.arduino_thread.stop()
        super().closeEvent(event)
            
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    palette = app.palette()
    palette.setColor(palette.Window, Qt.black)
    palette.setColor(palette.WindowText, Qt.white)
    app.setPalette(palette)
    
    window = MainApplication()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
