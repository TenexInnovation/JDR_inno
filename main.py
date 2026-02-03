import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from app import database as db
from app.admin_window import AdminWindow
from app.user_window import UserWindow

class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("JDR Badge Manager")
        self.setGeometry(200, 200, 450, 350)
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
            QLineEdit { 
                background-color: #2a2a2a; 
                border: 1px solid #444; 
                border-radius: 5px; 
                padding: 10px;
                color: #ffffff;
            }
            QFrame { background-color: #252525; border-radius: 10px; }
        """)
        
        db.init_database()
        
        self.admin_window = None
        self.user_window = None
        
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
        
        badge_frame = QFrame()
        badge_layout = QHBoxLayout(badge_frame)
        badge_layout.setContentsMargins(15, 15, 15, 15)
        
        badge_label = QLabel("Simulation Badge:")
        badge_label.setStyleSheet("color: #888888;")
        badge_layout.addWidget(badge_label)
        
        self.badge_entry = QLineEdit()
        self.badge_entry.setPlaceholderText("ID du badge...")
        self.badge_entry.returnPressed.connect(self.simulate_badge_scan)
        badge_layout.addWidget(self.badge_entry)
        
        scan_btn = QPushButton("Scanner")
        scan_btn.setObjectName("scan")
        scan_btn.clicked.connect(self.simulate_badge_scan)
        badge_layout.addWidget(scan_btn)
        
        main_layout.addWidget(badge_frame)
        
        main_layout.addStretch()
        
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
