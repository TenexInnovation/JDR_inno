from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QListWidget, QListWidgetItem, QComboBox,
    QFormLayout, QMessageBox, QFileDialog, QScrollArea, QFrame,
    QGridLayout, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import os
from app import database as db

class AdminWindow(QMainWindow):
    badge_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_badge_id = None
        self.setup_ui()
        self.refresh_character_list()
        
    def setup_ui(self):
        self.setWindowTitle("Administration - JDR Badge Manager")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; }
            QWidget { background-color: #1a1a1a; color: #ffffff; }
            QLabel { color: #ffffff; }
            QPushButton { 
                background-color: #2563eb; 
                color: white; 
                border: none; 
                padding: 10px 20px; 
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
            QPushButton#delete { background-color: #dc2626; }
            QPushButton#delete:hover { background-color: #b91c1c; }
            QPushButton#show { background-color: #16a34a; }
            QPushButton#show:hover { background-color: #15803d; }
            QPushButton#save { background-color: #16a34a; font-size: 16px; padding: 15px; }
            QLineEdit, QSpinBox, QComboBox { 
                background-color: #2a2a2a; 
                border: 1px solid #444; 
                border-radius: 5px; 
                padding: 8px;
                color: #ffffff;
            }
            QListWidget { 
                background-color: #2a2a2a; 
                border: 1px solid #444; 
                border-radius: 5px;
            }
            QListWidget::item { padding: 10px; }
            QListWidget::item:selected { background-color: #2563eb; }
            QFrame { background-color: #252525; border-radius: 10px; }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        
        title_label = QLabel("Liste des Personnages")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        left_layout.addWidget(title_label)
        
        self.character_list = QListWidget()
        self.character_list.itemClicked.connect(self.on_item_clicked)
        left_layout.addWidget(self.character_list)
        
        btn_layout = QHBoxLayout()
        
        new_btn = QPushButton("Nouveau")
        new_btn.clicked.connect(self.new_character)
        btn_layout.addWidget(new_btn)
        
        delete_btn = QPushButton("Supprimer")
        delete_btn.setObjectName("delete")
        delete_btn.clicked.connect(self.delete_character)
        btn_layout.addWidget(delete_btn)
        
        show_btn = QPushButton("Afficher")
        show_btn.setObjectName("show")
        show_btn.clicked.connect(self.show_in_user_view)
        btn_layout.addWidget(show_btn)
        
        left_layout.addLayout(btn_layout)
        main_layout.addWidget(left_frame, 1)
        
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        
        detail_title = QLabel("Détails du Personnage")
        detail_title.setFont(QFont("Arial", 16, QFont.Bold))
        right_layout.addWidget(detail_title)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.badge_id_edit = QLineEdit()
        self.badge_id_edit.setPlaceholderText("ID unique du badge")
        form_layout.addRow("ID Badge:", self.badge_id_edit)
        
        self.nom_perso_edit = QLineEdit()
        self.nom_perso_edit.setPlaceholderText("Nom du personnage")
        form_layout.addRow("Nom:", self.nom_perso_edit)
        
        file_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Fichier STL")
        file_layout.addWidget(self.file_path_edit)
        browse_btn = QPushButton("...")
        browse_btn.setMaximumWidth(40)
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        form_layout.addRow("Modèle 3D:", file_layout)
        
        right_layout.addLayout(form_layout)
        
        stats_label = QLabel("Statistiques")
        stats_label.setFont(QFont("Arial", 14, QFont.Bold))
        right_layout.addWidget(stats_label)
        
        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)
        
        self.stat_spins = {}
        stats = [
            ("Vigueur", 0, 0), ("Ruse", 0, 1),
            ("Agilité", 1, 0), ("Volonté", 1, 1),
            ("Intelligence", 2, 0), ("Présence", 2, 1)
        ]
        
        for stat_name, row, col in stats:
            label = QLabel(f"{stat_name}:")
            spin = QSpinBox()
            spin.setRange(1, 20)
            spin.setValue(5)
            self.stat_spins[stat_name.lower().replace("é", "e").replace("î", "i")] = spin
            stats_grid.addWidget(label, row, col * 2)
            stats_grid.addWidget(spin, row, col * 2 + 1)
            
        right_layout.addLayout(stats_grid)
        
        credits_layout = QHBoxLayout()
        credits_label = QLabel("Crédits:")
        self.credits_spin = QSpinBox()
        self.credits_spin.setRange(0, 100000)
        self.credits_spin.setValue(100)
        credits_layout.addWidget(credits_label)
        credits_layout.addWidget(self.credits_spin)
        credits_layout.addStretch()
        right_layout.addLayout(credits_layout)
        
        situation_layout = QHBoxLayout()
        situation_label = QLabel("Situation:")
        self.situation_combo = QComboBox()
        self.situation_combo.addItems(["recherche", "en_fuite", "RAS", "endette", "malfrat"])
        self.situation_combo.setCurrentText("RAS")
        situation_layout.addWidget(situation_label)
        situation_layout.addWidget(self.situation_combo)
        situation_layout.addStretch()
        right_layout.addLayout(situation_layout)
        
        right_layout.addStretch()
        
        save_btn = QPushButton("Enregistrer")
        save_btn.setObjectName("save")
        save_btn.clicked.connect(self.save_character)
        right_layout.addWidget(save_btn)
        
        main_layout.addWidget(right_frame, 1)
        
    def refresh_character_list(self):
        self.character_list.clear()
        characters = db.get_all_characters()
        
        for char in characters:
            badge_id = char[1]
            nom_perso = char[5] or "Sans nom"
            item = QListWidgetItem(f"{nom_perso} ({badge_id})")
            item.setData(Qt.UserRole, badge_id)
            self.character_list.addItem(item)
            
    def on_item_clicked(self, item):
        badge_id = item.data(Qt.UserRole)
        self.select_character(badge_id)
        
    def select_character(self, badge_id):
        self.selected_badge_id = badge_id
        char = db.get_character_by_badge(badge_id)
        
        if char:
            self.badge_id_edit.setText(char[1])
            self.file_path_edit.setText(char[4] or "")
            self.nom_perso_edit.setText(char[5] or "")
            
            stat_mapping = {
                'vigueur': char[6],
                'agilite': char[7],
                'intelligence': char[8],
                'ruse': char[9],
                'volonte': char[10],
                'presence': char[11]
            }
            
            for key, value in stat_mapping.items():
                if key in self.stat_spins:
                    self.stat_spins[key].setValue(value or 5)
                    
            self.credits_spin.setValue(char[17] or 100)
            self.situation_combo.setCurrentText(db.get_situation_from_row(char))
            
    def new_character(self):
        self.selected_badge_id = None
        self.badge_id_edit.clear()
        self.nom_perso_edit.clear()
        self.file_path_edit.clear()
        for spin in self.stat_spins.values():
            spin.setValue(5)
        self.credits_spin.setValue(100)
        self.situation_combo.setCurrentText("RAS")
        
    def browse_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un fichier STL", "3D",
            "STL files (*.stl);;All files (*.*)"
        )
        if filename:
            self.file_path_edit.setText(os.path.basename(filename))
            
    def save_character(self):
        badge_id = self.badge_id_edit.text().strip()
        nom_perso = self.nom_perso_edit.text().strip()
        file_path = self.file_path_edit.text().strip()
        
        if not badge_id or not nom_perso:
            QMessageBox.warning(self, "Erreur", 
                               "L'ID Badge et le nom du personnage sont obligatoires.")
            return
            
        vigueur = self.stat_spins['vigueur'].value()
        agilite = self.stat_spins['agilite'].value()
        intelligence = self.stat_spins['intelligence'].value()
        ruse = self.stat_spins['ruse'].value()
        volonte = self.stat_spins['volonte'].value()
        presence = self.stat_spins['presence'].value()
        credits = self.credits_spin.value()
        situation = self.situation_combo.currentText()
        
        existing = db.get_character_by_badge(badge_id)
        
        try:
            if existing:
                db.update_character(badge_id, file_path, nom_perso, vigueur, agilite,
                                   intelligence, ruse, volonte, presence, credits, situation)
                QMessageBox.information(self, "Succès", "Personnage mis à jour.")
            else:
                db.add_character(badge_id, file_path, nom_perso, vigueur, agilite,
                                intelligence, ruse, volonte, presence, credits, situation)
                QMessageBox.information(self, "Succès", "Personnage ajouté.")
                
            self.selected_badge_id = badge_id
            self.refresh_character_list()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
            
    def delete_character(self):
        if not self.selected_badge_id:
            QMessageBox.warning(self, "Attention", 
                               "Sélectionnez un personnage à supprimer.")
            return
            
        reply = QMessageBox.question(self, "Confirmation",
                                     "Êtes-vous sûr de vouloir supprimer ce personnage?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db.delete_character(self.selected_badge_id)
            self.new_character()
            self.refresh_character_list()
            
    def show_in_user_view(self):
        if self.selected_badge_id:
            self.badge_selected.emit(self.selected_badge_id)
