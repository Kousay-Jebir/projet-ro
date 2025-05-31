import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem, QTextEdit, QHeaderView, QMessageBox,
                             QLineEdit, QComboBox, QCheckBox)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt
import pulp

class PharmaSolver(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pharmaceutical Formulation Cost Optimizer")
        self.setMinimumSize(1400, 1100)  # Increased width and height for better table visibility
        self.ingredients = []
        # Theme colors (aligned with home.py)
        self.colors = {
            "primary": "#4a6da7",
            "secondary": "#6c5ce7",
            "success": "#00b894",
            "danger": "#d63031",
            "warning": "#fdcb6e",
            "dark": "#2d3436",
            "light": "#e9dfe1",
            "background": "#1e1e2e",
            "card": "#2a2a3a",
            "text": "#ffffff"
        }
        self.set_dark_theme()
        QApplication.instance().setStyleSheet(f'''
            QTableWidget, QTableView {{
                background-color: {self.colors['card']};
                color: {self.colors['text']};
                selection-background-color: {self.colors['primary']};
                selection-color: {self.colors['text']};
                gridline-color: {self.colors['dark']};
            }}
            QTableWidget QLineEdit, QTableView QLineEdit {{
                background-color: {self.colors['dark']};
                color: {self.colors['light']};
            }}
        ''')
        self.initUI()

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

    def darken_color(self, hex_color, percent):
        rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * (100 - percent) / 100)) for c in rgb)
        return '#%02x%02x%02x' % darkened

    def create_button(self, text, color):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(200, 55)
        btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 16px;
                font-size: 22px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color, 10)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 20)};
            }}
        ''')
        return btn

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("Pharmaceutical Formulation Optimizer")
        title.setStyleSheet(f"""
            font-size: 44px;
            font-weight: bold;
            color: {self.colors['primary']};
            padding-bottom: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Table for ingredients
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels([
            "Name", "Cost/kg", "Impurity %", "Toxicity %", "Biodisp %",
            "Stability (months)", "Min prop", "Max stock (kg)", "Include?"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {self.colors['primary']};
                color: {self.colors['text']};
                font-weight: bold;
                font-size: 18px;
            }}
        """)
        layout.addWidget(self.table)

        # Add default ingredients
        default_ingredients = [
            ["substance A", 10, 1.0, 0.5, 70, 12, 0.1, 700],
            ["substance B", 20, 0.8, 0.7, 60, 10, 0.05, 600],
            ["substance C", 15, 1.2, 0.6, 65, 8, 0.05, 500],
            ["excipient A", 25, 0.5, 0.4, 75, 14, 0.15, 800],
            ["excipient B", 30, 0.3, 0.2, 80, 16, 0.2, 900]
        ]
        for row in default_ingredients:
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)
            for col, value in enumerate(row):
                self.table.setItem(row_pos, col, QTableWidgetItem(str(value)))
            # Add checkbox in the last column
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox.setStyleSheet(f"margin-left:40%; margin-right:40%;")
            self.table.setCellWidget(row_pos, 8, checkbox)

        add_row_btn = self.create_button("Add Ingredient", self.colors["success"])
        add_row_btn.clicked.connect(self.add_row)
        layout.addWidget(add_row_btn)

        # Constraint table for user-friendly mix constraints
        constraint_label = QLabel("Mix Constraints:")
        constraint_label.setStyleSheet(f"font-size: 24px; color: {self.colors['primary']}; font-weight: bold;")
        layout.addWidget(constraint_label)
        self.constraint_table = QTableWidget(4, 2)
        self.constraint_table.setHorizontalHeaderLabels(["Constraint", "Value"])
        self.constraint_table.verticalHeader().setVisible(False)
        self.constraint_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.constraint_table.setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {self.colors['primary']};
                color: {self.colors['text']};
                font-weight: bold;
                font-size: 16px;
            }}
        """)
        # Predefined constraints
        self.predefined_constraints = [
            ("Max Impurity (%)", 2.5),
            ("Max Toxicity (%)", 2.0),
            ("Min Biodisp (%)", 60),
            ("Min Stability (months)", 6),
            ("Min Impurity (%)", 0.0),
            ("Min Toxicity (%)", 0.0)
        ]
        constraint_names = [c[0] for c in self.predefined_constraints[:4]]
        default_values = [c[1] for c in self.predefined_constraints[:4]]
        for i, (name, val) in enumerate(zip(constraint_names, default_values)):
            self.constraint_table.setItem(i, 0, QTableWidgetItem(name))
            self.constraint_table.setItem(i, 1, QTableWidgetItem(str(val)))
        layout.addWidget(self.constraint_table)

        # Dropdown and button to add more constraints
        add_constraint_layout = QHBoxLayout()
        self.constraint_dropdown = QComboBox()
        self.constraint_dropdown.addItems([c[0] for c in self.predefined_constraints[4:]])
        self.constraint_dropdown.setFixedWidth(200)
        self.constraint_dropdown.setStyleSheet(f"""
            QComboBox {{
                font-size: 16px;
                padding: 4px 8px;
                background-color: {self.colors['card']};
                color: {self.colors['text']};
                border-radius: 6px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.colors['card']};
                color: {self.colors['text']};
            }}
        """)
        add_constraint_btn = self.create_button("Add Constraint", self.colors["secondary"])
        add_constraint_btn.setFixedWidth(180)
        add_constraint_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {self.colors['secondary']};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 4px 8px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(self.colors['secondary'], 10)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(self.colors['secondary'], 20)};
            }}
        ''')
        add_constraint_btn.clicked.connect(self.add_constraint_row)
        add_constraint_layout.addWidget(self.constraint_dropdown)
        add_constraint_layout.addWidget(add_constraint_btn)
        layout.addLayout(add_constraint_layout)

        # Total quantity input
        total_label = QLabel("Total Quantity (kg):")
        total_label.setStyleSheet(f"font-size: 20px; color: {self.colors['primary']}; font-weight: bold;")
        layout.addWidget(total_label)
        self.total_quantity_input = QLineEdit()
        self.total_quantity_input.setText("1")
        self.total_quantity_input.setFixedWidth(120)
        self.total_quantity_input.setStyleSheet(f"""
            background-color: {self.colors['dark']};
            color: {self.colors['light']};
            border-radius: 6px;
            font-size: 18px;
            padding: 4px 8px;
        """)
        layout.addWidget(self.total_quantity_input)

        # Solve button
        solve_btn = self.create_button("Solve", self.colors["primary"])
        solve_btn.clicked.connect(self.solve)
        layout.addWidget(solve_btn)

        # Results output
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setFont(QFont("Courier", 14))
        self.result_output.setStyleSheet(f"""
            background-color: {self.colors['card']};
            color: {self.colors['success']};
            border-radius: 8px;
            font-size: 18px;
            padding: 10px;
        """)
        layout.addWidget(self.result_output)

        central_widget.setLayout(layout)

    def add_row(self):
        row_pos = self.table.rowCount()
        self.table.insertRow(row_pos)
        for col in range(8):
            self.table.setItem(row_pos, col, QTableWidgetItem(""))
        checkbox = QCheckBox()
        checkbox.setChecked(True)
        checkbox.setStyleSheet(f"margin-left:40%; margin-right:40%;")
        self.table.setCellWidget(row_pos, 8, checkbox)

    def add_constraint_row(self):
        # Add a new constraint row from dropdown if not already present
        selected = self.constraint_dropdown.currentText()
        for i in range(self.constraint_table.rowCount()):
            if self.constraint_table.item(i, 0) and self.constraint_table.item(i, 0).text() == selected:
                QMessageBox.warning(self, "Constraint Exists", f"'{selected}' already exists.")
                return
        row_pos = self.constraint_table.rowCount()
        self.constraint_table.insertRow(row_pos)
        self.constraint_table.setItem(row_pos, 0, QTableWidgetItem(selected))
        # Set default value from predefined list
        for c in self.predefined_constraints:
            if c[0] == selected:
                self.constraint_table.setItem(row_pos, 1, QTableWidgetItem(str(c[1])))
                break

    def solve(self):
        try:
            # Ensure all edits in the constraint table are committed
            self.constraint_table.clearSelection()
            self.constraint_table.clearFocus()
            QApplication.processEvents()

            n = self.table.rowCount()
            names, cost, impurity, toxicity, biodisp, stability = [], [], [], [], [], []
            min_prop, stock = [], []
            include_rows = []

            for i in range(n):
                checkbox = self.table.cellWidget(i, 8)
                if checkbox is not None and not checkbox.isChecked():
                    continue
                include_rows.append(i)
                names.append(self.table.item(i, 0).text())
                cost.append(float(self.table.item(i, 1).text()))
                impurity.append(float(self.table.item(i, 2).text()))
                toxicity.append(float(self.table.item(i, 3).text()))
                biodisp.append(float(self.table.item(i, 4).text()))
                stability.append(float(self.table.item(i, 5).text()))
                min_prop.append(float(self.table.item(i, 6).text()))
                stock.append(float(self.table.item(i, 7).text()))

            if not names:
                self.result_output.setText("No ingredients selected for inclusion.")
                return

            # Read constraints from the table (supporting min/max for impurity/toxicity)
            constraint_map = {}
            for i in range(self.constraint_table.rowCount()):
                key = self.constraint_table.item(i, 0).text()
                val = float(self.constraint_table.item(i, 1).text())
                constraint_map[key] = val
            max_impurity = constraint_map.get("Max Impurity (%)", 2.5)
            min_impurity = constraint_map.get("Min Impurity (%)", None)
            max_toxicity = constraint_map.get("Max Toxicity (%)", 2.0)
            min_toxicity = constraint_map.get("Min Toxicity (%)", None)
            min_biodisp = constraint_map.get("Min Biodisp (%)", 60)
            min_stability = constraint_map.get("Min Stability (months)", 6)

            # Read total quantity from input
            total_quantity = float(self.total_quantity_input.text())

            model = pulp.LpProblem("DrugFormulation", pulp.LpMinimize)
            # Set variable bounds as proportions of total_quantity
            x = [
                pulp.LpVariable(
                    f"x{j}",
                    lowBound=min_prop[j] * total_quantity,
                    upBound=stock[j]
                )
                for j in range(len(names))
            ]

            model += pulp.lpSum([cost[j] * x[j] for j in range(len(names))]), "TotalCost"
            model += pulp.lpSum([x[j] for j in range(len(names))]) == total_quantity, "TotalWeight"
            model += pulp.lpSum([impurity[j] * x[j] for j in range(len(names))]) <= max_impurity * total_quantity
            if min_impurity is not None:
                model += pulp.lpSum([impurity[j] * x[j] for j in range(len(names))]) >= min_impurity * total_quantity
            model += pulp.lpSum([toxicity[j] * x[j] for j in range(len(names))]) <= max_toxicity * total_quantity
            if min_toxicity is not None:
                model += pulp.lpSum([toxicity[j] * x[j] for j in range(len(names))]) >= min_toxicity * total_quantity
            model += pulp.lpSum([biodisp[j] * x[j] for j in range(len(names))]) >= min_biodisp * total_quantity
            model += pulp.lpSum([stability[j] * x[j] for j in range(len(names))]) >= min_stability * total_quantity

            # Diagnostic output for debugging infeasibility
            diagnostic = 'DIAGNOSTIC INFO\n'
            diagnostic += f'Total quantity: {total_quantity} kg\n'
            diagnostic += 'Ingredient bounds (min in kg, stock):\n'
            for j in range(len(names)):
                diagnostic += f"  {names[j]}: min={min_prop[j]*total_quantity:.2f}, stock={stock[j]}\n"
            diagnostic += f"Max impurity: {max_impurity}\n"
            diagnostic += f"Min impurity: {min_impurity}\n"
            diagnostic += f"Max toxicity: {max_toxicity}\n"
            diagnostic += f"Min toxicity: {min_toxicity}\n"
            diagnostic += f"Min biodisp: {min_biodisp}\n"
            diagnostic += f"Min stability: {min_stability}\n\n"
            self.result_output.setText(diagnostic)

            status = model.solve()
            if status != pulp.LpStatusOptimal:
                self.result_output.setText("Aucune solution optimale trouvée.")
                return

            result_text = f"\nTotal Cost: {pulp.value(model.objective):.2f}\n"
            for j in range(len(names)):
                result_text += f"{names[j]}: {x[j].varValue:.4f} kg\n"

            self.result_output.setText(result_text)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PharmaSolver()
    window.show()
    sys.exit(app.exec_())