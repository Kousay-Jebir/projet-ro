from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QFrame, 
                            QMessageBox, QFileDialog, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon
import networkx as nx
import sys
import re
from gurobi_solver import GurobiSolver

class GraphEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph Editor Pro")
        self.setMinimumSize(1200, 800)
        
        # Custom color palette
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
        
        # Set dark theme
        self.set_dark_theme()
        
        self.graph = nx.Graph()
        self.start_node = None
        self.end_node = None
        
        self.init_ui()
        self.solver = GurobiSolver(self.graph, self.statusBar(), self.result_text, None, None)
        
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
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Left sidebar
        sidebar = QFrame()
        sidebar.setFrameShape(QFrame.StyledPanel)
        sidebar.setMinimumWidth(300)
        sidebar.setMaximumWidth(350)
        sidebar.setStyleSheet(f"background-color: {self.colors['card']}; border-radius: 10px;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 15, 15, 15)
        sidebar_layout.setSpacing(15)
        
        # Node operations
        node_group, node_content = self.create_card("NODE OPERATIONS")
        self.node_name_widget, self.node_name_entry = self.create_input("Node Name:", placeholder="Enter node name")
        add_node_btn = self.create_button("Add Node", self.colors["success"], icon="➕", 
                                action=self.add_node, tooltip="Add a new node to the graph")
        node_content.layout.addWidget(self.node_name_widget)
        node_content.layout.addWidget(add_node_btn)
        
        # Edge operations
        edge_group, edge_content = self.create_card("EDGE OPERATIONS")
        self.edge_nodes_widget, self.edge_nodes_entry = self.create_input("Nodes (A,B):", placeholder="Enter connected nodes")
        self.edge_weight_widget, self.edge_weight_entry = self.create_input("Weight:", placeholder="Enter edge weight")
        add_edge_btn = self.create_button("Add Edge", self.colors["primary"], icon="🔗", 
                                        action=self.add_edge, tooltip="Add a new edge between nodes")
        edge_content.layout.addWidget(self.edge_nodes_widget)
        edge_content.layout.addWidget(self.edge_weight_widget)
        edge_content.layout.addWidget(add_edge_btn)
        
        # Add widgets to sidebar
        sidebar_layout.addWidget(node_group)
        sidebar_layout.addWidget(edge_group)
        sidebar_layout.addStretch()
                
        # Right content area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(15)
        
        # Tables area
        tables_widget = QWidget()
        tables_layout = QHBoxLayout(tables_widget)
        tables_layout.setContentsMargins(0, 0, 0, 0)
        tables_layout.setSpacing(15)
        
        # Nodes table
        nodes_card, nodes_content = self.create_card("NODES")
        self.nodes_table = self.create_table(["Node"])
        nodes_content.layout.addWidget(self.nodes_table)

        
        # Edges table
        edges_card, edges_content = self.create_card("EDGES")
        self.edges_table = self.create_table(["From", "To", "Weight"])
        edges_content.layout.addWidget(self.edges_table)

        tables_layout.addWidget(nodes_card)
        tables_layout.addWidget(edges_card)
        
        # Path finding
        path_card, path_content = self.create_card("SHORTEST PATH")
        path_layout = QHBoxLayout()
        path_content.layout.addLayout(path_layout)

        self.start_node_combobox = QComboBox()
        self.start_node_combobox.setPlaceholderText("Start node")
        self.start_node_combobox.setStyleSheet(self.get_combo_style())

        self.end_node_combobox = QComboBox()
        self.end_node_combobox.setPlaceholderText("End node")
        self.end_node_combobox.setStyleSheet(self.get_combo_style())

        solve_btn = self.create_button("Solve", self.colors["secondary"], icon="🚀", 
                                    action=self.solve_graph, tooltip="Find shortest path")

        path_layout.addWidget(self.start_node_combobox)
        path_layout.addWidget(self.end_node_combobox)
        path_layout.addWidget(solve_btn)
        
        # Results area
        result_card, result_content = self.create_card("RESULTS")
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.colors['card']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['dark']};
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas';
            }}
        """)
        result_content.layout.addWidget(self.result_text)
        
        # Add widgets to content area
        content_layout.addWidget(tables_widget)
        content_layout.addWidget(path_card)
        content_layout.addWidget(result_card)
        
        # Add sidebar and content to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)
        
        # Status bar
        self.statusBar().setStyleSheet(f"""
            QStatusBar {{
                background-color: {self.colors['dark']};
                color: {self.colors['text']};
                border-top: 1px solid {self.colors['card']};
            }}
        """)
        
    def create_card(self, title):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['card']};
                border-radius: 10px;
            }}
        """)
        
        # Main layout for the card
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)
        
        # Title label
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['primary']};
                font-weight: bold;
                font-size: 14px;
            }}
        """)
        card_layout.addWidget(title_label)
        
        # Create a container widget for the card content
        content_widget = QWidget()
        card_layout.addWidget(content_widget)
        
        # Store the content layout as an attribute
        content_widget.layout = QVBoxLayout(content_widget)
        content_widget.layout.setContentsMargins(0, 0, 0, 0)
        content_widget.layout.setSpacing(10)
        
        return card, content_widget
    def create_input(self, label_text, placeholder=""):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(label_text)
        label.setStyleSheet(f"color: {self.colors['text']};")
        
        entry = QLineEdit()
        entry.setPlaceholderText(placeholder)
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
        
        # Store the entry as an attribute of the widget
        widget.entry = entry
        return widget, entry
    def create_button(self, text, color, icon="", action=None, tooltip=""):
        btn = QPushButton(f"{icon} {text}" if icon else text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                min-width: 100px;
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
    
    def create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
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
    
    def get_combo_style(self):
        return f"""
            QComboBox {{
                background-color: {self.colors['card']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['dark']};
                border-radius: 5px;
                padding: 8px;
                min-width: 100px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.colors['card']};
                color: {self.colors['text']};
                selection-background-color: {self.colors['primary']};
            }}
        """
    
    def darken_color(self, hex_color, percent):
        """Darken a hex color by a percentage"""
        rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * (100 - percent) / 100)) for c in rgb)
        return '#%02x%02x%02x' % darkened
    
    # ===== Core Functionality (unchanged from original) =====
    def validate_node_name(self, node_name):
        return bool(node_name and re.match(r'^[a-zA-Z0-9_-]+$', node_name))

    def validate_edge_weight(self, weight):
        try:
            return float(weight) >= 0
        except ValueError:
            return False

    def add_node(self):
        node_name = self.node_name_entry.text()
        if self.validate_node_name(node_name):
            if node_name not in self.graph:
                self.graph.add_node(node_name)
                self.update_node_list()
                self.node_name_entry.clear()
                self.show_status("Node added successfully", False)
            else:
                self.show_status("Node already exists")
        else:
            self.show_status("Invalid node name. Use only letters, numbers, hyphens and underscores.")

    def add_edge(self):
        edge_input = self.edge_nodes_entry.text()
        weight_input = self.edge_weight_entry.text()
        if edge_input and weight_input:
            nodes = [n.strip() for n in edge_input.split(',')]
            if len(nodes) == 2 and nodes[0] in self.graph and nodes[1] in self.graph:
                if self.validate_edge_weight(weight_input):
                    weight = float(weight_input)
                    self.graph.add_edge(nodes[0], nodes[1], weight=weight)
                    self.update_edge_list()
                    self.edge_nodes_entry.clear()
                    self.edge_weight_entry.clear()
                    self.show_status("Edge added successfully", False)
                else:
                    self.show_status("Weight must be a positive number")
            else:
                self.show_status("Both nodes must exist in the graph")
        else:
            self.show_status("Please fill all fields")

    def update_node_list(self):
        self.nodes_table.setRowCount(0)
        for node in self.graph.nodes:
            row = self.nodes_table.rowCount()
            self.nodes_table.insertRow(row)
            self.nodes_table.setItem(row, 0, QTableWidgetItem(node))
        
        nodes = list(self.graph.nodes)
        self.start_node_combobox.clear()
        self.end_node_combobox.clear()
        self.start_node_combobox.addItems(nodes)
        self.end_node_combobox.addItems(nodes)

    def update_edge_list(self):
        self.edges_table.setRowCount(0)
        for u, v, d in self.graph.edges(data=True):
            row = self.edges_table.rowCount()
            self.edges_table.insertRow(row)
            self.edges_table.setItem(row, 0, QTableWidgetItem(u))
            self.edges_table.setItem(row, 1, QTableWidgetItem(v))
            self.edges_table.setItem(row, 2, QTableWidgetItem(str(d["weight"])))

    def show_status(self, message, is_error=True):
        self.statusBar().showMessage(message)
        if is_error:
            self.statusBar().setStyleSheet(f"color: {self.colors['danger']};")
        else:
            self.statusBar().setStyleSheet(f"color: {self.colors['success']};")

    def solve_graph(self):
        start = self.start_node_combobox.currentText()
        end = self.end_node_combobox.currentText()
        if start in self.graph and end in self.graph:
            self.start_node = start
            self.end_node = end
            self.solver.start_node = start
            self.solver.end_node = end
            self.solver.solve()
        else:
            self.show_status("Please select valid start and end nodes")

    def load_graph(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Graph", "", "CSV Files (*.csv)")
        if path:
            with open(path) as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row)==1: 
                        self.graph.add_node(row[0])
                    elif len(row)==3: 
                        self.graph.add_edge(row[0], row[1], weight=float(row[2]))
            self.update_node_list()
            self.update_edge_list()
            self.show_status("Graph loaded successfully", False)

    def save_graph(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Graph", "", "CSV Files (*.csv)")
        if path:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                for n in self.graph.nodes: 
                    writer.writerow([n])
                for u, v, d in self.graph.edges(data=True): 
                    writer.writerow([u, v, d['weight']])
            self.show_status("Graph saved successfully", False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = GraphEditor()
    window.show()
    sys.exit(app.exec_())