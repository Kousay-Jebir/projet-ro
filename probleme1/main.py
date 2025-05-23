from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QFrame, 
                            QMessageBox, QFileDialog, QSizePolicy, QDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon
import networkx as nx
import sys
import re, csv
from .gurobi_solver import GurobiSolver
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class GraphViewDialog(QDialog):
    def __init__(self, graph, colors=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Graph View")
        self.resize(600, 500)
        self.graph = graph
        self.colors = colors or {
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
        layout = QVBoxLayout(self)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.draw_graph()

    def draw_graph(self):
        self.ax.clear()
        self.ax.set_facecolor(self.colors['background'])  # Set background color
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, ax=self.ax, with_labels=True, node_color=self.colors['primary'], edge_color=self.colors['secondary'], font_color=self.colors['text'])
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, ax=self.ax, font_color=self.colors['warning'])
        self.canvas.draw()

class GraphEditor(QMainWindow):
    def __init__(self, home_window=None):
        super().__init__()
        self.home_window = home_window 
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
        
        self.graph = nx.DiGraph()
        self.start_node = None
        self.end_node = None
        # self.init_return_button()
        
        self.init_ui()
        self.solver = GurobiSolver(self.graph, self.statusBar(), self.result_text, None, None)
    
    def return_to_home(self):
        """Return to home screen"""
        self.close()
        if hasattr(self, 'home_window') and self.home_window:
            self.home_window.show()
            self.home_window.activateWindow()
    def init_ui(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_vertical_layout = QVBoxLayout(central_widget)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        main_vertical_layout.setSpacing(0)


        content_area=QWidget()
        main_layout = QHBoxLayout(content_area)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        top_bar = QWidget()
        top_bar.setFixedHeight(50)
        top_bar.setStyleSheet(f"background-color: {self.colors['dark']};")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(10, 0, 10, 0)

        self.return_btn = self.create_button("← Return to Home", self.colors["primary"])
        self.return_btn.clicked.connect(self.return_to_home)
        self.return_btn.setFixedSize(180, 50)
        top_layout.addStretch()
        top_layout.addWidget(self.return_btn)
        
        main_vertical_layout.addWidget(top_bar)
        
        
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

        matrix_btn = self.create_button("Matrix Input", self.colors["warning"], icon="🧮",
                                        action=self.open_matrix_input, tooltip="Define relations using a matrix")
        edge_content.layout.addWidget(matrix_btn)

        show_graph_btn = self.create_button("Show Graph", self.colors["secondary"], icon="🖼️", action=self.show_graph_view, tooltip="Visualize the current graph")
        edge_content.layout.addWidget(show_graph_btn)

        csv_group, csv_content = self.create_card("CSV OPERATIONS")
        add_csv_btn = self.create_button("Load CSV", self.colors["primary"], icon="📂", 
                                        action=self.load_graph, tooltip="load a csv file")
        csv_content.layout.addWidget(add_csv_btn)
        save_csv_btn = self.create_button("Save CSV", self.colors["primary"], icon="💾", 
                                        action=self.save_graph, tooltip="save a csv file")
        csv_content.layout.addWidget(save_csv_btn)
        
        # Add widgets to sidebar
        sidebar_layout.addWidget(node_group)
        sidebar_layout.addWidget(edge_group)
        sidebar_layout.addWidget(csv_group)
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
        main_vertical_layout.addWidget(content_area)
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
                background-color: {self.darken_color(color, 10)}
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 20)}
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
                background-color: {self.colors['dark']};
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
            try:
                with open(path) as f:
                    # Debug: Print raw content
                    content = f.read()
                    print(f"File content:\n{content}")
                    f.seek(0)
                    
                    # Process file
                    reader = csv.reader(f)
                    self.graph.clear()  # Clear existing graph
                    
                    for row in reader:
                        if not row:  # Skip empty lines
                            continue
                        if len(row) == 1: 
                            self.graph.add_node(row[0].strip())
                        elif len(row) == 3: 
                            try:
                                weight = float(row[2])
                                self.graph.add_edge(row[0].strip(), row[1].strip(), weight=weight)
                            except ValueError:
                                print(f"Skipping invalid edge weight: {row[2]}")
                
                # Debug: Verify graph state
                print("Final nodes:", self.graph.nodes())
                print("Final edges:", self.graph.edges(data=True))
                
                # Update UI
                self.update_node_list()
                self.update_edge_list()
                
                # Force refresh
                self.nodes_table.resizeColumnsToContents()
                self.edges_table.resizeColumnsToContents()
                
                self.show_status("Graph loaded successfully", False)
                
            except Exception as e:
                self.show_status(f"Error loading file: {str(e)}")
                print(f"Error: {e}")       
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
    def open_matrix_input(self):
        nodes = list(self.graph.nodes)
        if not nodes:
            QMessageBox.warning(self, "Warning", "No nodes to create matrix for.")
            return
    
        dialog = MatrixInputDialog(nodes, self, colors=self.colors, graph=self.graph)
        if dialog.exec_() == QDialog.Accepted:
            matrix = dialog.get_matrix()
            self.graph.remove_edges_from(list(self.graph.edges))  # Clear previous edges
            for (u, v), w in matrix.items():
                self.graph.add_edge(u, v, weight=w)
    
            self.refresh_edges_table()
            self.statusBar().showMessage("Edges updated via matrix.", 5000)
    def refresh_edges_table(self):
        self.edges_table.setRowCount(0)
        for u, v, data in self.graph.edges(data=True):
            row_pos = self.edges_table.rowCount()
            self.edges_table.insertRow(row_pos)
            self.edges_table.setItem(row_pos, 0, QTableWidgetItem(str(u)))
            self.edges_table.setItem(row_pos, 1, QTableWidgetItem(str(v)))
            self.edges_table.setItem(row_pos, 2, QTableWidgetItem(str(data.get("weight", ""))))

    def show_graph_view(self):
        dialog = GraphViewDialog(self.graph, colors=self.colors, parent=self)
        dialog.exec_()

class MatrixInputDialog(QDialog):
    def __init__(self, nodes, parent=None, colors=None, graph=None):
        super().__init__(parent)
        self.setWindowTitle("Matrix Input")
        self.resize(500, 400)
        self.nodes = nodes
        self.colors = colors or {
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
        self.graph = graph

        layout = QVBoxLayout(self)

        self.table = QTableWidget(len(nodes), len(nodes))
        self.table.setHorizontalHeaderLabels(nodes)
        self.table.setVerticalHeaderLabels(nodes)
        layout.addWidget(self.table)

        # Apply custom dark style to the dialog and table
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.colors['background']};
            }}
            QTableWidget {{
                background-color: {self.colors['card']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['dark']};
                gridline-color: {self.colors['dark']};
                selection-background-color: {self.colors['primary']};
                selection-color: {self.colors['text']};
            }}
            QHeaderView::section {{
                background-color: {self.colors['dark']};
                color: {self.colors['text']};
                font-weight: bold;
                border: none;
            }}
            QPushButton {{
                background-color: {self.colors['primary']};
                color: {self.colors['text']};
                border: none;
                border-radius: 5px;
                padding: 8px 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.colors['secondary']};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['success']};
            }}
        """)

        # Initialize all cells to '0' to avoid empty cell warnings
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                self.table.setItem(i, j, QTableWidgetItem("0"))

        # Pre-fill with current graph weights if provided
        if self.graph is not None:
            for u, v, data in self.graph.edges(data=True):
                if u in self.nodes and v in self.nodes:
                    i = self.nodes.index(u)
                    j = self.nodes.index(v)
                    self.table.setItem(i, j, QTableWidgetItem(str(data.get("weight", "0"))))

        button_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def get_matrix(self):
        matrix = {}
        for i, from_node in enumerate(self.nodes):
            for j, to_node in enumerate(self.nodes):
                item = self.table.item(i, j)
                if item:
                    try:
                        weight = float(item.text())
                        if weight != 0:
                            matrix[(from_node, to_node)] = weight
                    except ValueError:
                        continue
        return matrix



if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = GraphEditor()
    window.show()
    sys.exit(app.exec_())