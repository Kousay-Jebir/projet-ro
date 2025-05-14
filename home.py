import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette
from PyQt5.QtCore import Qt

class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optimization Problems Solver")
        self.setMinimumSize(1400, 1000)
        
        # Custom color palette matching problem1/main.py
        self.colors = {
            "primary": "#4a6da7",
            "secondary": "#6c5ce7",
            "success": "#00b894",
            "danger": "#d63031",
            "warning": "#fdcb6e",
            "dark": "#2d3436",
            "light": "#dfe6e9",
            "background": "#1e1e2e",
            "card": "#2a2a3a",
            "text": "#ffffff"
        }
        
        self.set_dark_theme()
        self.init_ui()
    
    def set_dark_theme(self):
        """Apply the dark theme palette"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(self.colors["background"]))
        palette.setColor(QPalette.WindowText, QColor(self.colors["text"]))
        palette.setColor(QPalette.Base, QColor(self.colors["card"]))
        palette.setColor(QPalette.AlternateBase, QColor(self.colors["dark"]))
        palette.setColor(QPalette.ToolTipBase, QColor(self.colors["dark"]))
        palette.setColor(QPalette.ToolTipText, QColor(self.colors["text"]))
        palette.setColor(QPalette.Text, QColor(self.colors["text"]))
        palette.setColor(QPalette.Button, QColor(self.colors["primary"]))
        palette.setColor(QPalette.ButtonText, QColor(self.colors["text"]))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Highlight, QColor(self.colors["secondary"]))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        QApplication.setPalette(palette)
    
    def init_ui(self):
        """Initialize the user interface"""
        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(30)
        
        # Title
        title = QLabel("Select Problem")
        title.setStyleSheet(f"""
            font-size: 56px; 
            font-weight: bold;
            color: {self.colors['primary']};
            padding-bottom: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Buttons container
        buttons_container = QHBoxLayout()
        buttons_container.setSpacing(80)
        buttons_container.setContentsMargins(0, 0, 0, 0)
        
        # Problem 1 (Shortest Path)
        problem1_card = self.create_problem_card(
            "assets/graph.png",
            "Shortest Path Problem",
            "Find optimal paths in networks"
        )
        problem1_btn = self.create_button("Open Solver", self.colors["primary"])
        problem1_btn.clicked.connect(self.open_shortest_path)
        problem1_card.button_layout.addWidget(problem1_btn)
        
        # Problem 2 (Resource Management)
        problem2_card = self.create_problem_card(
            "assets/ressource.png",
            "Resource Management",
            "Optimize resource allocation"
        )
        problem2_btn = self.create_button("Open Solver", self.colors["primary"])
        problem2_btn.clicked.connect(self.open_resource_mgmt)
        problem2_card.button_layout.addWidget(problem2_btn)
        
        # Add cards to container
        buttons_container.addWidget(problem1_card)
        buttons_container.addWidget(problem2_card)
        main_layout.addLayout(buttons_container)
        
        # Set application font
        font = QFont("Segoe UI", 10)
        self.setFont(font)
    
    def create_problem_card(self, icon_path, title, description):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setFixedSize(500, 700)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['card']};
                border-radius: 12px;
                border: 1px solid {self.colors['dark']};
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(30)

        icon = QLabel()
        pixmap = QPixmap(icon_path)
        icon.setPixmap(pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(f"""
            QLabel {{
                padding: 10px;
                border-radius: 90px;
                background-color: {self.darken_color(self.colors['card'], 5)};
                border: 1px solid {self.colors['dark']};
            }}
        """)
        layout.addWidget(icon)
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 40px; 
            font-weight: bold;
            color: {self.colors['primary']};
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            font-size: 20px; 
            font-weight: bold;
            color: {self.colors['light']};
            padding: 0 10px;
        """)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        # Button container to ensure proper centering
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignCenter)
        
        
        layout.addWidget(button_container)
        
        # Store the button layout so we can add button later
        card.button_layout = button_layout
        
        return card
    
    def create_button(self, text, color):
        """Create a styled button"""
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(220, 70)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 16px;
                font-size: 26px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color, 10)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 20)};
            }}
        """)
        return btn
    
    def darken_color(self, hex_color, percent):
        """Darken a hex color by a percentage"""
        rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * (100 - percent) / 100)) for c in rgb)
        return '#%02x%02x%02x' % darkened
    
    def open_shortest_path(self):
        try:
            project_root = str(Path(__file__).parent)
            if project_root not in sys.path:
                sys.path.append(project_root)

            from probleme1.main import GraphEditor
            self.solver = GraphEditor(home_window=self)
            self.solver.show()
            self.hide()
        except Exception as e:
            print(e)
            QMessageBox.critical(self, "Error", 
                f"Failed to load shortest path solver:\n{str(e)}\n"
                f"Python path: {sys.path}\n"
                f"Current dir: {Path.cwd()}"
            )
    def open_resource_mgmt(self):
        try:
            project_root = str(Path(__file__).parent)
            if project_root not in sys.path:
                sys.path.append(project_root)
            
            from probleme2.main import ResourceAllocator
            self.solver = ResourceAllocator(home_window=self)  # Pass self as home_window
            self.solver.show()
            self.hide()
        except Exception as e:
            print(e)
            QMessageBox.critical(self, "Error", f"Failed to load resource allocator:\n{str(e)}")
    def show_returned(self):
        """Show the home window when returning from a solver"""
        self.show()
        self.activateWindow()
        self.raise_()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    sys.exit(app.exec_())