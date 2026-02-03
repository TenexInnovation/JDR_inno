from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
import os
from app import database as db

try:
    import vtk
    from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
    VTK_AVAILABLE = True
except ImportError:
    VTK_AVAILABLE = False

class StatBubble(QFrame):
    def __init__(self, stat_name, parent=None):
        super().__init__(parent)
        self.stat_name = stat_name
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedSize(100, 130)
        self.setStyleSheet("""
            QFrame { 
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(5)
        
        self.bubble = QFrame()
        self.bubble.setFixedSize(80, 80)
        self.bubble.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 2px solid #444;
                border-radius: 40px;
            }
        """)
        
        bubble_layout = QVBoxLayout(self.bubble)
        bubble_layout.setAlignment(Qt.AlignCenter)
        
        self.value_label = QLabel("--")
        self.value_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet("color: #ffffff; background: transparent; border: none;")
        bubble_layout.addWidget(self.value_label)
        
        layout.addWidget(self.bubble, alignment=Qt.AlignCenter)
        
        self.name_label = QLabel(self.stat_name)
        self.name_label.setFont(QFont("Arial", 11))
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("color: #888888; background: transparent;")
        layout.addWidget(self.name_label)
        
    def set_value(self, value):
        self.value_label.setText(str(value))
        
        if value >= 8:
            color = "#00ff00"
        elif value >= 6:
            color = "#88ff00"
        elif value >= 4:
            color = "#ffff00"
        elif value >= 2:
            color = "#ff8800"
        else:
            color = "#ff0000"
            
        self.value_label.setStyleSheet(f"color: {color}; background: transparent; border: none;")


class VTKWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rotation_angle = 0
        self.actor = None
        self.renderer = None
        self.vtk_widget = None
        self.rotation_timer = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if not VTK_AVAILABLE:
            self.fallback_label = QLabel("VTK non disponible\n\nInstallez vtk avec:\npip install vtk")
            self.fallback_label.setFont(QFont("Arial", 14))
            self.fallback_label.setAlignment(Qt.AlignCenter)
            self.fallback_label.setStyleSheet("color: #888888; background: transparent;")
            layout.addWidget(self.fallback_label)
            return
            
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        layout.addWidget(self.vtk_widget)
        
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.1, 0.1, 0.1)
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        
        self.setup_lighting()
        
        self.rotation_timer = QTimer(self)
        self.rotation_timer.timeout.connect(self.rotate_model)
        
        self.vtk_widget.Initialize()
        self.vtk_widget.Start()
        
    def setup_lighting(self):
        if not self.renderer:
            return
            
        light1 = vtk.vtkLight()
        light1.SetFocalPoint(0, 0, 0)
        light1.SetPosition(1, 1, 1)
        light1.SetColor(1.0, 1.0, 1.0)
        light1.SetIntensity(0.8)
        self.renderer.AddLight(light1)
        
        light2 = vtk.vtkLight()
        light2.SetFocalPoint(0, 0, 0)
        light2.SetPosition(-1, -0.5, -1)
        light2.SetColor(0.4, 0.4, 0.6)
        light2.SetIntensity(0.4)
        self.renderer.AddLight(light2)
        
    def show_placeholder_text(self, text=None):
        if not VTK_AVAILABLE or not self.renderer:
            return
            
        self.clear_scene()
        self.vtk_widget.GetRenderWindow().Render()
        
    def load_stl(self, file_path):
        if not VTK_AVAILABLE or not self.renderer:
            return False
            
        if not os.path.exists(file_path):
            self.show_placeholder_text(f"Fichier non trouvé:\n{file_path}")
            return False
            
        self.clear_scene()
        
        try:
            reader = vtk.vtkSTLReader()
            reader.SetFileName(file_path)
            reader.Update()
            
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(reader.GetOutputPort())
            
            self.actor = vtk.vtkActor()
            self.actor.SetMapper(mapper)
            
            self.actor.GetProperty().SetColor(0.3, 0.6, 0.9)
            self.actor.GetProperty().SetSpecular(0.4)
            self.actor.GetProperty().SetSpecularPower(30)
            self.actor.GetProperty().SetAmbient(0.2)
            self.actor.GetProperty().SetDiffuse(0.8)
            
            self.actor.RotateX(-90)
            
            self.renderer.AddActor(self.actor)
            self.renderer.ResetCamera()
            
            camera = self.renderer.GetActiveCamera()
            camera.Azimuth(0)
            camera.Elevation(10)
            camera.Zoom(0.85)
            
            self.vtk_widget.GetRenderWindow().Render()
            
            self.rotation_angle = 0
            self.rotation_timer.start(50)
            
            return True
            
        except Exception as e:
            self.show_placeholder_text(f"Erreur de chargement:\n{str(e)}")
            return False
            
    def rotate_model(self):
        if not self.actor or not self.renderer:
            return
            
        self.rotation_angle += 0.5
        self.actor.SetOrientation(-90, 0, self.rotation_angle)
        self.vtk_widget.GetRenderWindow().Render()
        
    def clear_scene(self):
        if self.rotation_timer:
            self.rotation_timer.stop()
            
        if self.renderer:
            self.renderer.RemoveAllViewProps()
            self.actor = None
            
    def stop_rotation(self):
        if self.rotation_timer:
            self.rotation_timer.stop()
            
    def closeEvent(self, event):
        self.stop_rotation()
        if self.vtk_widget:
            self.vtk_widget.Finalize()
        super().closeEvent(event)


class UserWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_badge_id = None
        self.current_character = None
        self.vtk_widget = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("JDR - Vue Personnage")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow { background-color: #0a0a0a; }
            QWidget { background-color: transparent; }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        self.name_label = QLabel("Aucun personnage sélectionné")
        self.name_label.setFont(QFont("Arial", 36, QFont.Bold))
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("color: #ffffff;")
        main_layout.addWidget(self.name_label)
        
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        left_stats = QWidget()
        left_layout = QVBoxLayout(left_stats)
        left_layout.setAlignment(Qt.AlignCenter)
        left_layout.setSpacing(10)
        
        self.left_bubbles = {}
        for stat_name in ["Vigueur", "Présence", "Agilité"]:
            bubble = StatBubble(stat_name)
            self.left_bubbles[stat_name] = bubble
            left_layout.addWidget(bubble)
            
        content_layout.addWidget(left_stats)
        
        center_frame = QFrame()
        center_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #333;
                border-radius: 20px;
            }
        """)
        center_frame.setMinimumSize(500, 400)
        center_layout = QVBoxLayout(center_frame)
        center_layout.setContentsMargins(10, 10, 10, 10)
        
        self.vtk_widget = VTKWidget()
        center_layout.addWidget(self.vtk_widget)
        
        self.model_label = QLabel("")
        self.model_label.setFont(QFont("Arial", 10))
        self.model_label.setAlignment(Qt.AlignCenter)
        self.model_label.setStyleSheet("color: #666666; background: transparent; border: none;")
        self.model_label.setMaximumHeight(30)
        center_layout.addWidget(self.model_label)
        
        content_layout.addWidget(center_frame, stretch=2)
        
        right_stats = QWidget()
        right_layout = QVBoxLayout(right_stats)
        right_layout.setAlignment(Qt.AlignCenter)
        right_layout.setSpacing(10)
        
        self.right_bubbles = {}
        for stat_name in ["Intelligence", "Volonté", "Ruse"]:
            bubble = StatBubble(stat_name)
            self.right_bubbles[stat_name] = bubble
            right_layout.addWidget(bubble)
            
        content_layout.addWidget(right_stats)
        
        main_layout.addLayout(content_layout, stretch=1)
        
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(50)
        
        self.situation_frame = QFrame()
        self.situation_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #444;
                border-radius: 25px;
                padding: 10px;
            }
        """)
        self.situation_frame.setMinimumWidth(250)
        situation_layout = QVBoxLayout(self.situation_frame)
        
        self.situation_label = QLabel("Situation: ---")
        self.situation_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.situation_label.setAlignment(Qt.AlignCenter)
        self.situation_label.setStyleSheet("color: #ffffff; background: transparent; border: none;")
        situation_layout.addWidget(self.situation_label)
        
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.situation_frame)
        bottom_layout.addStretch()
        
        self.credits_frame = QFrame()
        self.credits_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #444;
                border-radius: 25px;
                padding: 10px;
            }
        """)
        self.credits_frame.setMinimumWidth(200)
        credits_layout = QVBoxLayout(self.credits_frame)
        
        self.credits_label = QLabel("Crédits: --- $")
        self.credits_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.credits_label.setAlignment(Qt.AlignCenter)
        self.credits_label.setStyleSheet("color: #00ff00; background: transparent; border: none;")
        credits_layout.addWidget(self.credits_label)
        
        bottom_layout.addWidget(self.credits_frame)
        bottom_layout.addStretch()
        
        main_layout.addLayout(bottom_layout)
        
    def display_character(self, badge_id):
        self.current_badge_id = badge_id
        self.current_character = db.get_character_by_badge(badge_id)
        
        if not self.current_character:
            self.name_label.setText("Personnage non trouvé")
            self.vtk_widget.show_placeholder_text("Personnage non trouvé")
            return
            
        char = self.current_character
        
        self.name_label.setText(char[5] or "Sans nom")
        
        stat_mapping_left = {
            "Vigueur": char[6],
            "Présence": char[11],
            "Agilité": char[7]
        }
        
        stat_mapping_right = {
            "Intelligence": char[8],
            "Volonté": char[10],
            "Ruse": char[9]
        }
        
        for stat_name, value in stat_mapping_left.items():
            self.left_bubbles[stat_name].set_value(value or 0)
            
        for stat_name, value in stat_mapping_right.items():
            self.right_bubbles[stat_name].set_value(value or 0)
            
        situation = db.get_situation_from_row(char)
        situation_display = db.get_situation_display(situation)
        self.situation_label.setText(f"Situation: {situation_display}")
        
        situation_colors = {
            "recherche": "#ff4444",
            "en_fuite": "#ff8800",
            "RAS": "#44ff44",
            "endette": "#ffff00",
            "malfrat": "#ff00ff"
        }
        color = situation_colors.get(situation, "#1a1a1a")
        self.situation_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: 2px solid {color};
                border-radius: 25px;
                padding: 10px;
            }}
        """)
        
        if situation in ["RAS"]:
            self.situation_label.setStyleSheet("color: #000000; background: transparent; border: none;")
        elif situation in ["endette"]:
            self.situation_label.setStyleSheet("color: #000000; background: transparent; border: none;")
        else:
            self.situation_label.setStyleSheet("color: #ffffff; background: transparent; border: none;")
        
        credits = char[17] or 0
        self.credits_label.setText(f"Crédits: {credits} $")
        
        file_path = char[4]
        if file_path:
            if file_path.startswith("3D/") or file_path.startswith("3D\\"):
                full_path = file_path
            else:
                full_path = os.path.join("3D", file_path)
                
            if os.path.exists(full_path):
                self.model_label.setText(f"Modèle: {os.path.basename(file_path)}")
                self.vtk_widget.load_stl(full_path)
            else:
                self.model_label.setText(f"Modèle non trouvé: {file_path}")
                self.vtk_widget.show_placeholder_text(f"Fichier 3D non trouvé:\n{file_path}")
        else:
            self.model_label.setText("Aucun modèle 3D associé")
            self.vtk_widget.show_placeholder_text("Aucun modèle 3D\nassocié à ce personnage")
            
    def closeEvent(self, event):
        if self.vtk_widget:
            self.vtk_widget.stop_rotation()
        super().closeEvent(event)
