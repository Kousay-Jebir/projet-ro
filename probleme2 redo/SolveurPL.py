import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit,
                             QPushButton, QTextEdit, QMessageBox, QHBoxLayout, QFormLayout,
                             QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy)
from PyQt5.QtGui import QPixmap, QFont, QBrush, QPalette, QColor
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
# from PL import solve_lp
from gurobipy import GRB
import importlib.util
import os

# Dynamically import PL from the same directory as this file
spec = importlib.util.spec_from_file_location("PL", os.path.join(os.path.dirname(__file__), "PL.py"))
PL = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PL)
solve_lp = PL.solve_lp

class LPApp(QMainWindow):
    def __init__(self, home_window=None):
        super().__init__()
        self.home_window = home_window
        self.setWindowTitle("Solveur de Problèmes de Programmation Linéaire")
        self.setMinimumSize(1600, 1000)
        # Modern color palette matching home.py
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
        self.initUI()
        self.setWindowIcon(QtGui.QIcon('sus.png'))

    def set_dark_theme(self):
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

    def initUI(self):
        self.setAutoFillBackground(True)
        palette = self.palette()
        # Remove background image, use background color
        palette.setColor(QPalette.Window, QColor(self.colors["background"]))
        self.setPalette(palette)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Add Title
        self.title_label = self.createStyledLabel("Solveur de Problèmes de Programmation Linéaire", 24)
        self.layout.addWidget(self.title_label, alignment=Qt.AlignCenter)
        self.layout.addSpacing(20)

        # Variable Names and Coefficients Section
        self.layout.addWidget(self.createStyledLabel("Ajouter des Variables et des Coefficients", 18))

        self.var_coef_layout = QFormLayout()
        self.variable_input = self.createStyledLineEdit()
        self.coefficient_input = self.createStyledLineEdit()
        self.add_variable_button = self.createStyledButton("Ajouter Variable", self.add_variable, color="#2979FF")
        self.var_coef_layout.addRow(self.createStyledLabel("Nom de Variable:", 14), self.variable_input)
        self.var_coef_layout.addRow(self.createStyledLabel("Coefficient:", 14), self.coefficient_input)
        self.var_coef_layout.addWidget(self.add_variable_button)
        self.layout.addLayout(self.var_coef_layout)

        # Variables and Coefficients Display
        self.variables_layout = QVBoxLayout()
        self.layout.addLayout(self.variables_layout)

        # Constraints Section
        self.layout.addWidget(self.createStyledLabel("Contraintes", 18))
        self.constraints_table = QTableWidget(self)
        self.constraints_table.setStyleSheet(self.createTableStyle())
        self.constraints_table.setFont(QFont("Trebuchet MS", 14, QFont.Bold))
        self.layout.addWidget(self.constraints_table)

        self.add_constraint_button = self.createStyledButton("Ajouter Contrainte", self.add_constraint_row, color="#2979FF")
        self.layout.addWidget(self.add_constraint_button)

        # Objective Type Section
        self.objective_type_layout = QFormLayout()
        self.objective_type_input = self.createStyledComboBox()
        self.objective_type_input.addItems(["Minimiser", "Maximiser"])
        self.objective_type_layout.addRow(self.createStyledLabel("Type d'objectif:", 14), self.objective_type_input)
        self.layout.addLayout(self.objective_type_layout)

        # Solve Button
        self.solve_button = self.createStyledButton("Résoudre", self.solve_lp, color="#2979FF")
        self.layout.addWidget(self.solve_button)

        # Reset Button
        self.reset_button = self.createStyledButton("Réinitialiser", self.reset_form, color="#f44336")
        self.layout.addWidget(self.reset_button)

        # Center buttons
        self.center_buttons([self.add_variable_button, self.add_constraint_button, self.solve_button, self.reset_button])

        # Result Section
        self.result_label = self.createStyledLabel("Résultats:", 18)
        self.layout.addWidget(self.result_label)

        self.result_output = QTextEdit(self)
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet(
            "color: #F5F6FA; background-color: #23272F; border: 2px solid #3A3F4B; border-radius: 5px; padding: 10px;")
        self.result_output.setFont(QFont("Trebuchet MS", 14, QFont.Bold))
        self.layout.addWidget(self.result_output)

        self.variable_names = []
        self.coefficients = []

        # Add Back to Home button if home_window is provided
        if self.home_window is not None:
            self.back_button = self.createStyledButton("Retour à l'accueil", self.back_to_home, color="#6c5ce7")
            self.layout.addWidget(self.back_button)
            self.layout.setAlignment(self.back_button, Qt.AlignCenter)

    def back_to_home(self):
        self.close()
        if self.home_window is not None:
            self.home_window.show_returned()

    def createStyledLabel(self, text, font_size):
        label = QLabel(text, self)
        label.setStyleSheet(f"color: {self.colors['text']}; font-family: 'Segoe UI'; font-size: {font_size}px; font-weight: bold;")
        label.setAlignment(Qt.AlignCenter)
        return label

    def createStyledLineEdit(self):
        line_edit = QLineEdit(self)
        line_edit.setStyleSheet(
            f"color: {self.colors['text']}; background-color: {self.colors['card']}; border: 2px solid {self.colors['dark']}; border-radius: 5px; padding: 5px;")
        line_edit.setFont(QFont("Segoe UI", 14, QFont.Bold))
        return line_edit

    def createStyledButton(self, text, callback, color=None):
        base_color = color if color else self.colors['primary']
        darker_color = self.darken_color(base_color, 10)
        even_darker_color = self.darken_color(base_color, 20)
        button = QPushButton(text, self)
        button.setStyleSheet(f"""
            QPushButton {{
                color: {self.colors['text']};
                background-color: {base_color};
                border: none;
                border-radius: 10px;
                padding: 8px 16px;
                font-size: 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {darker_color};
            }}
            QPushButton:pressed {{
                background-color: {even_darker_color};
            }}
        """)
        button.setFont(QFont("Segoe UI", 14, QFont.Bold))
        button.clicked.connect(callback)
        return button

    def darken_color(self, hex_color, percent):
        rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * (100 - percent) / 100)) for c in rgb)
        return '#%02x%02x%02x' % darkened

    def createStyledComboBox(self):
        combo_box = QComboBox(self)
        combo_box.setStyleSheet(f"""
            QComboBox {{
                color: {self.colors['text']};
                background-color: {self.colors['card']};
                border: 2px solid {self.colors['dark']};
                border-radius: 5px;
                padding: 5px;
            }}
            QComboBox:hover {{
                background-color: {self.darken_color(self.colors['card'], 5)};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: {self.colors['dark']};
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }}
            QComboBox QAbstractItemView {{
                color: {self.colors['text']};
                background-color: {self.colors['card']};
                selection-background-color: {self.colors['primary']};
                border: 1px solid {self.colors['dark']};
            }}
        """)
        combo_box.setFont(QFont("Segoe UI", 14, QFont.Bold))
        return combo_box

    def createTableStyle(self):
        return f"""
            QTableWidget {{
                background-color: {self.colors['card']};
                border: 2px solid {self.colors['dark']};
                border-radius: 5px;
                color: {self.colors['text']};
                font-size: 14px;
                font-weight: bold;
                gridline-color: {self.colors['primary']};
            }}
            QHeaderView::section {{
                background-color: {self.colors['primary']};
                color: {self.colors['text']};
                border: none;
                font-weight: bold;
            }}
        """

    def center_buttons(self, buttons):
        for button in buttons:
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.layout.setAlignment(button, Qt.AlignCenter)

    def add_variable(self):
        nom_variable = self.variable_input.text().strip()
        try:
            coefficient = float(self.coefficient_input.text().strip())
        except ValueError:
            QMessageBox.critical(self, "Erreur", "Le coefficient doit être un nombre valide.", QMessageBox.Ok)
            return

        if nom_variable and nom_variable not in self.variable_names:
            self.variable_names.append(nom_variable)
            self.coefficients.append(coefficient)
            self.update_variables_display()
            self.update_table_columns()
            self.variable_input.clear()
            self.coefficient_input.clear()
        else:
            QMessageBox.critical(self, "Erreur", "Le nom de la variable doit être unique et non vide.", QMessageBox.Ok)

    def update_variables_display(self):
        for i in reversed(range(self.variables_layout.count())):
            item = self.variables_layout.itemAt(i)
            if item.widget() is not None:
                item.widget().deleteLater()

        for name, coef in zip(self.variable_names, self.coefficients):
            hbox = QHBoxLayout()
            label = QLabel(f"{name} (Coefficient: {coef})", self)
            label.setStyleSheet("color: #F5F6FA; font-family: 'Trebuchet MS'; font-size: 14px; font-weight: bold;")
            hbox.addWidget(label)
            container = QWidget()
            container.setLayout(hbox)
            self.variables_layout.addWidget(container)

    def update_table_columns(self):
        num_vars = len(self.variable_names)

        self.constraints_table.setColumnCount(num_vars + 2)
        headers = self.variable_names + ['Sens', 'Valeur Limite']
        self.constraints_table.setHorizontalHeaderLabels(headers)
        self.constraints_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Update each row to have the correct number of columns
        for row in range(self.constraints_table.rowCount()):
            for col in range(self.constraints_table.columnCount()):
                if col == num_vars:
                    sense_combo = self.createStyledComboBox()
                    sense_combo.addItems(["<=", ">=", "=="])
                    self.constraints_table.setCellWidget(row, col, sense_combo)
                elif self.constraints_table.item(row, col) is None:
                    self.constraints_table.setItem(row, col, QTableWidgetItem("0"))

    def add_constraint_row(self):
        row_position = self.constraints_table.rowCount()
        self.constraints_table.insertRow(row_position)
        for col in range(self.constraints_table.columnCount()):
            if col == len(self.variable_names):
                sense_combo = self.createStyledComboBox()
                sense_combo.addItems(["<=", ">=", "=="])
                self.constraints_table.setCellWidget(row_position, col, sense_combo)
            else:
                self.constraints_table.setItem(row_position, col, QTableWidgetItem("0"))

    def reset_form(self):
        self.variable_input.clear()
        self.coefficient_input.clear()
        self.variable_names.clear()
        self.coefficients.clear()
        self.update_variables_display()
        self.constraints_table.clearContents()
        self.constraints_table.setRowCount(0)
        self.update_table_columns()
        self.result_output.clear()

    def solve_lp(self):
        try:
            if len(self.variable_names) != len(self.coefficients):
                raise ValueError("Le nombre de noms de variables doit correspondre au nombre de coefficients.")

            A = []
            b = []
            sens = []
            for row in range(self.constraints_table.rowCount()):
                A.append([float(self.constraints_table.item(row, col).text()) for col in range(len(self.variable_names))])
                sens.append(self.constraints_table.cellWidget(row, len(self.variable_names)).currentText())
                b.append(float(self.constraints_table.item(row, len(self.variable_names) + 1).text()))

            objective_type = GRB.MINIMIZE if self.objective_type_input.currentText().lower() == 'minimiser' else GRB.MAXIMIZE

            result = PL.solve_lp(self.variable_names, self.coefficients, A, b, sens, objective_type)

            if result["objective_value"] is not None:
                result_text = f"Valeur optimale de l'objectif: {result['objective_value']}\n"
                for var, value in result["variables"].items():
                    result_text += f"{var}: {value}\n"
            else:
                result_text = "Aucune solution optimale trouvée."

            self.result_output.setText(result_text)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e), QMessageBox.Ok)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = LPApp()
    main_window.show()
    sys.exit(app.exec_())
