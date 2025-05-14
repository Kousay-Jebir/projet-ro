import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem, QFileDialog,
    QHeaderView, QFrame, QSizePolicy, QMainWindow
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
import csv
from .resource_solver import ResourceSolver

class ResourceAllocator(QMainWindow):
    def __init__(self, home_window=None):
        super().__init__()
        self.home_window = home_window 
        self.setWindowTitle("📊 Resource Allocation Minimizer")
        self.setMinimumSize(1800, 1000)
        self.costs = []
        self.constraints = []
        
        # Modern color palette
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
    # def init_return_button(self):
    #     """Initialize the return to home button"""
    #     return_btn = QPushButton("← Home", self)
    #     return_btn.setFixedSize(100, 30)
    #     return_btn.move(10, 10)
    #     return_btn.setStyleSheet("""
    #         QPushButton {
    #             background-color: #4a6da7;
    #             color: white;
    #             border: none;
    #             border-radius: 4px;
    #             padding: 5px;
    #             font-size: 12px;
    #         }
    #         QPushButton:hover {
    #             background-color: #5a7db7;
    #         }
    #     """)
    #     return_btn.clicked.connect(self.return_to_home)
    #     return_btn.setCursor(Qt.PointingHandCursor)
        
    def return_to_home(self):
        """Return to home screen"""
        self.close()
        if hasattr(self, 'home_window') and self.home_window:
            self.home_window.show()
            self.home_window.activateWindow()
        
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

    def init_ui(self):
        # Main layout with sidebar and content area
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_vertical_layout = QVBoxLayout(central_widget)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        main_vertical_layout.setSpacing(0)

        content_area= QWidget()    
        main_layout = QHBoxLayout(content_area)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        top_bar = QWidget()
        top_bar.setFixedHeight(80)
        top_bar.setStyleSheet(f"background-color: {self.colors['dark']};")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(10, 0, 10, 0)

        self.return_btn = self.create_button("← Return to Home", self.colors["primary"])
        self.return_btn.setFixedSize(180, 50)
        self.return_btn.clicked.connect(self.return_to_home)
        top_layout.addStretch()
        top_layout.addWidget(self.return_btn)
        
        main_vertical_layout.addWidget(top_bar)
        sidebar = QWidget()
        sidebar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(10)
        
        # Right content area (tables and results)
        content = QWidget()
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)
        
        # Set fixed ratio (1:3)
        main_layout.addWidget(sidebar, stretch=1)  # Sidebar gets 1 part
        main_layout.addWidget(content, stretch=2) 
        main_vertical_layout.addWidget(content_area) # Content gets 3 parts
        
        # 1. ADD COST section in sidebar
        cost_card = self.create_card("💰 ADD COST")
        self.cost_input = self.create_input("Cost:", placeholder="Enter cost value")
        add_cost_btn = self.create_button("➕ Add Cost", self.colors["success"], 
                                        action=self.add_cost, tooltip="Add a cost value")
        cost_card.layout().addWidget(self.cost_input)
        cost_card.layout().addWidget(add_cost_btn)
        
        # 2. ADD CONSTRAINTS section in sidebar
        constraint_card = self.create_card("🔗 ADD CONSTRAINTS")
        self.a_ij_input = self.create_input("a_ij:", placeholder="Comma separated values")
        self.b_j_input = self.create_input("b_j:", placeholder="Constraint value")
        add_constraint_btn = self.create_button("➕ Add Constraint", self.colors["success"], 
                                            action=self.add_constraint, tooltip="Add a constraint")
        constraint_card.layout().addWidget(self.a_ij_input)
        constraint_card.layout().addWidget(self.b_j_input)
        constraint_card.layout().addWidget(add_constraint_btn)
        
        # 3. LOAD CSV section in sidebar
        file_card = self.create_card("📂 FILE OPERATIONS")
        load_csv_btn = self.create_button("📂 Load CSV", self.colors["primary"], 
                                        action=self.load_all_data, tooltip="Load data from CSV")
        save_csv_btn = self.create_button("💾 Save CSV", self.colors["primary"], 
                                        action=self.save_all_data, tooltip="Save data to CSV")
        file_card.layout().addWidget(load_csv_btn)
        file_card.layout().addWidget(save_csv_btn)
        
        # 4. SOLVE/CLEAR section in sidebar
        action_card = self.create_card("⚡ ACTIONS")
        self.demand_input = self.create_input("Min Demand:", initial_value="5.0")
        solve_btn = self.create_button("🚀 Solve", self.colors["secondary"], 
                                    action=self.solve, tooltip="Solve the optimization problem")
        clear_btn = self.create_button("🧹 Clear All", self.colors["danger"], 
                                    action=self.clear_all, tooltip="Clear all inputs")
        action_card.layout().addWidget(self.demand_input)
        action_card.layout().addWidget(solve_btn)
        action_card.layout().addWidget(clear_btn)
        
        # Add all sidebar cards with stretch factors
        sidebar_layout.addWidget(cost_card)
        sidebar_layout.addWidget(constraint_card)
        sidebar_layout.addWidget(file_card)
        sidebar_layout.addWidget(action_card)
          # Push all cards to the top
        
        # CONTENT AREA COMPONENTS
        # 1. COSTS TABLE
        cost_table_card = self.create_card("📝 COSTS TABLE")
        self.cost_table = self.create_table(["Costs"], rows=1)
        cost_table_card.layout().addWidget(self.cost_table)
        
        # 2. CONSTRAINTS TABLE
        constraint_table_card = self.create_card("📋 CONSTRAINTS TABLE")
        self.constraint_table = self.create_table(["a_0", "a_1", "...", "b_j"])
        constraint_table_card.layout().addWidget(self.constraint_table)
        
        # 3. RESULTS
        result_card = self.create_card("📊 RESULTS")
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.colors['card']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['dark']};
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas';
            }}
        """)
        result_card.layout().addWidget(self.result_output)
        
        # Error label
        self.error_label = QLabel()
        self.error_label.setStyleSheet(f"color: {self.colors['danger']};")
        self.error_label.setAlignment(Qt.AlignCenter)
        
        # Add content area components with stretch factors
        content_layout.addWidget(cost_table_card, stretch=1)
        content_layout.addWidget(constraint_table_card, stretch=1)
        content_layout.addWidget(result_card, stretch=1)  
        content_layout.addWidget(self.error_label)
    def create_card(self, title):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        card.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['card']};
                border-radius: 10px;
                padding: 5px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['primary']};
                font-weight: bold;
                font-size: 14px;
                padding-bottom: 5px;
            }}
        """)
        layout.addWidget(title_label)
        
        return card
    def create_input(self, label_text, placeholder="", initial_value=""):
        widget = QWidget()
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(label_text)
        label.setStyleSheet(f"color: {self.colors['text']};")
        
        entry = QLineEdit()
        entry.setPlaceholderText(placeholder)
        if initial_value:
            entry.setText(initial_value)
        entry.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.colors['card']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['dark']};
                border-radius: 5px;
                padding: 8px;
            }}
        """)
        
        layout.addWidget(label)
        layout.addWidget(entry)
        
        widget.entry = entry
        return widget
    def create_button(self, text, color, action=None, tooltip=""):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color, 10)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 20)};
            }}
        """)
        
        if action:
            btn.clicked.connect(action)
        if tooltip:
            btn.setToolTip(tooltip)
            
        return btn
    def create_table(self, headers, rows=0):
        table = QTableWidget(rows, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {self.colors['card']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['dark']};
                border-radius: 5px;
                gridline-color: {self.colors['dark']};
            }}
            QHeaderView::section {{
                background-color: {self.colors['dark']};
                color: {self.colors['text']};
                padding: 5px;
                border: none;
            }}
        """)
        return table

    def darken_color(self, hex_color, percent):
        """Darken a hex color by a percentage"""
        rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * (100 - percent) / 100)) for c in rgb)
        return '#%02x%02x%02x' % darkened
    def add_cost(self):
        try:
            value = float(self.cost_input.entry.text())
            self.costs.append(value)
            
            # Clear and rebuild the entire cost table each time
            self.cost_table.clear()
            self.cost_table.setRowCount(1)
            self.cost_table.setColumnCount(len(self.costs))
            
            # Add all costs (including the new one)
            for col, cost in enumerate(self.costs):
                item = QTableWidgetItem(str(cost))
                item.setTextAlignment(Qt.AlignCenter) 
                self.cost_table.setItem(0, col, item)
                
            self.cost_input.entry.clear()
            self.update_constraint_headers()
            self.error_label.setText("")
        except ValueError:
            self.error_label.setText("Invalid cost value")
    def add_constraint(self):
        try:
            a_ij = list(map(float, self.a_ij_input.entry.text().split(',')))
            b_j = float(self.b_j_input.entry.text())
            if len(a_ij) != len(self.costs):
                self.error_label.setText("Length of a_ij must match number of costs")
                return
            self.constraints.append((a_ij, b_j))
            row = self.constraint_table.rowCount()
            col_count = len(self.costs) + 1
            self.constraint_table.setColumnCount(col_count)
            self.constraint_table.setRowCount(row + 1)
            for i in range(len(a_ij)):
                item = QTableWidgetItem(str(a_ij[i]))
                item.setTextAlignment(Qt.AlignCenter)  # Center alignment
                self.constraint_table.setItem(row, i, item)
            b_item = QTableWidgetItem(str(b_j))
            b_item.setTextAlignment(Qt.AlignCenter)  # Center alignment
            self.constraint_table.setItem(row, len(a_ij), b_item)
            self.a_ij_input.entry.clear()
            self.b_j_input.entry.clear()
            self.error_label.setText("")
        except ValueError:
            self.error_label.setText("Invalid constraint format")

    
    def update_constraint_headers(self):
        """Update table headers and ensure they remain visible"""
        # Always show headers, even for empty tables
        cost_headers = [f"c_{i}" for i in range(len(self.costs) or 1)]  # Show at least one header
        constraint_headers = [f"a_{i}" for i in range(len(self.costs) or 1)] + ["b_j"]
        
        # Cost table headers
        self.cost_table.setColumnCount(len(cost_headers))
        self.cost_table.setHorizontalHeaderLabels(cost_headers)
        
        # Constraint table headers
        self.constraint_table.setColumnCount(len(constraint_headers))
        self.constraint_table.setHorizontalHeaderLabels(constraint_headers)
        
        # Force headers to be visible
        self.cost_table.horizontalHeader().show()
        self.constraint_table.horizontalHeader().show()
    def solve(self):
        try:
            demand = float(self.demand_input.entry.text())
            solver = ResourceSolver(self.costs, self.constraints, self.error_label, self.result_output, demand)
            solver.solve()
        except Exception as e:
            self.error_label.setText(str(e))

    def clear_all(self):
       
        # Clear the data structures
        self.costs = []
        self.constraints = []
        
        # Clear the table contents but preserve structure
        self.cost_table.clearContents()
        self.constraint_table.clearContents()
        
        # Set up empty tables with correct headers
        self.cost_table.setRowCount(1)
        self.cost_table.setColumnCount(0)  # Will be updated below
        
        self.constraint_table.setRowCount(0)
        self.constraint_table.setColumnCount(0)  # Will be updated below
        
        # Force header update and visibility
        self.update_constraint_headers()
        
        # Clear other UI elements
        self.error_label.setText("")
        self.result_output.clear()
    def load_all_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, newline='') as f:
                reader = csv.reader(f)
                rows = list(reader)

                # First row = costs
                self.costs = list(map(float, rows[0]))
                self.cost_table.clear()
                self.cost_table.setRowCount(1)
                self.cost_table.setColumnCount(len(self.costs))
                for i, cost in enumerate(self.costs):
                    item = QTableWidgetItem(str(cost))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.cost_table.setItem(0, i, item)

                # Reset and load constraints
                self.constraints = []
                self.constraint_table.clear()
                self.constraint_table.setRowCount(len(rows)-1)  # Set all rows at once
                self.constraint_table.setColumnCount(len(self.costs) + 1)  # +1 for b_j
                
                for i, row in enumerate(rows[1:]):
                    a_ij = list(map(float, row[:-1]))
                    b_j = float(row[-1])
                    self.constraints.append((a_ij, b_j))
                    
                    # Add all constraint values for this row
                    for j, val in enumerate(a_ij + [b_j]):
                        item = QTableWidgetItem(str(val))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.constraint_table.setItem(i, j, item)

                self.update_constraint_headers()
                self.error_label.setText("")
        except Exception as e:
            self.error_label.setText(f"Failed to load CSV: {e}")
    def save_all_data(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.costs)
                for a_ij, b_j in self.constraints:
                    writer.writerow(a_ij + [b_j])
            self.error_label.setText("")
        except Exception as e:
            self.error_label.setText(f"Failed to save CSV: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = ResourceAllocator()
    window.show()
    sys.exit(app.exec_())