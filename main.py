import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import simpledialog
from tkinter import ttk
import networkx as nx
import csv
import re
from gurobi_solver import GurobiSolver

class GraphEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Editor")
        self.graph = nx.Graph()  # Créer un graphe vide
        self.start_node = None
        self.end_node = None

        # Redimensionner la fenêtre pour un look plus moderne
        self.root.geometry('800x800')
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=2)

        self.create_widgets()

    def create_widgets(self):
        # Frame pour ajouter un nœud
        self.add_node_frame = ttk.LabelFrame(self.root, text="Ajouter un Nœud", padding="10")
        self.add_node_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.node_name_entry = ttk.Entry(self.add_node_frame)
        self.node_name_entry.grid(row=0, column=0, padx=5, sticky="ew")
        self.add_node_button = ttk.Button(self.add_node_frame, text="Ajouter", command=self.add_node)
        self.add_node_button.grid(row=0, column=1, padx=5)

        # Frame pour ajouter une arête
        self.add_edge_frame = ttk.LabelFrame(self.root, text="Ajouter une Arête", padding="10")
        self.add_edge_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.edge_nodes_entry = ttk.Entry(self.add_edge_frame)
        self.edge_nodes_entry.grid(row=0, column=0, padx=5, sticky="ew")
        self.edge_weight_entry = ttk.Entry(self.add_edge_frame)
        self.edge_weight_entry.grid(row=0, column=1, padx=5, sticky="ew")
        self.add_edge_button = ttk.Button(self.add_edge_frame, text="Ajouter", command=self.add_edge)
        self.add_edge_button.grid(row=0, column=2, padx=5)

        # Zone pour sélectionner les nœuds de départ et d'arrivée
        self.select_nodes_frame = ttk.LabelFrame(self.root, text="Sélectionner les Nœuds pour le Plus Court Chemin", padding="10")
        self.select_nodes_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.start_node_combobox = ttk.Combobox(self.select_nodes_frame)
        self.start_node_combobox.grid(row=0, column=0, padx=5, sticky="ew")
        self.start_node_combobox.set("Sélectionner un nœud de départ")

        self.end_node_combobox = ttk.Combobox(self.select_nodes_frame)
        self.end_node_combobox.grid(row=0, column=1, padx=5, sticky="ew")
        self.end_node_combobox.set("Sélectionner un nœud d'arrivée")

        # Frame pour les listes de nœuds et arêtes
        self.list_frame = ttk.Frame(self.root)
        self.list_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Liste pour afficher les nœuds
        self.nodes_listbox = tk.Listbox(self.list_frame, height=10, width=30)
        self.nodes_listbox.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Liste pour afficher les arêtes
        self.edges_listbox = tk.Listbox(self.list_frame, height=10, width=30)
        self.edges_listbox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Zone d'affichage des erreurs
        self.error_label = ttk.Label(self.root, text="", foreground="red")
        self.error_label.grid(row=2, column=0, columnspan=3, pady=5)

        # Boutons pour charger et sauvegarder le graphe
        self.load_button = ttk.Button(self.root, text="Charger le graphe", command=self.load_graph)
        self.load_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.save_button = ttk.Button(self.root, text="Sauvegarder le graphe", command=self.save_graph)
        self.save_button.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # Boutons pour modifier et supprimer nœuds/arêtes
        self.modify_node_button = ttk.Button(self.root, text="Modifier Nœud", command=self.modify_node)
        self.modify_node_button.grid(row=3, column=2, padx=10, pady=10, sticky="ew")

        self.delete_node_button = ttk.Button(self.root, text="Supprimer Nœud", command=self.delete_node)
        self.delete_node_button.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        self.modify_edge_button = ttk.Button(self.root, text="Modifier Arête", command=self.modify_edge)
        self.modify_edge_button.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

        self.delete_edge_button = ttk.Button(self.root, text="Supprimer Arête", command=self.delete_edge)
        self.delete_edge_button.grid(row=4, column=2, padx=10, pady=10, sticky="ew")

        # Bouton pour résoudre avec Gurobi
        self.solve_button = ttk.Button(self.root, text="Résoudre", command=self.solve_graph)
        self.solve_button.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Zone pour afficher les résultats de Gurobi
        self.result_text = tk.Text(self.root, height=10, width=50, wrap=tk.WORD, state=tk.DISABLED)
        self.result_text.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

        # Initialisation du solveur
        self.solver = GurobiSolver(self.graph, self.error_label, self.result_text, self.start_node, self.end_node)

    def solve_graph(self):
        start_node = self.start_node_combobox.get()
        end_node = self.end_node_combobox.get()

        if start_node == "Sélectionner un nœud de départ" or end_node == "Sélectionner un nœud d'arrivée":
            self.display_error("Veuillez sélectionner à la fois un nœud de départ et un nœud d'arrivée.")
        else:
            # Passer les nœuds de départ et d'arrivée à la méthode de GurobiSolver
            self.start_node = start_node
            self.end_node = end_node
            self.solver.start_node = self.start_node
            self.solver.end_node = self.end_node
            self.solver.solve()


    def display_error(self, message):
        self.error_label.config(text=message)

    def validate_node_name(self, node_name):
        """ Valide que le nom du nœud est une chaîne non vide et ne contient que des caractères valides. """
        if not node_name or not re.match(r'^[a-zA-Z0-9_-]+$', node_name):
            return False
        return True

    def validate_edge_weight(self, weight):
        """ Valide que le poids de l'arête est un nombre valide (positif). """
        try:
            weight = float(weight)
            return weight >= 0
        except ValueError:
            return False

    def add_node(self):
        node_name = self.node_name_entry.get()
        if self.validate_node_name(node_name):
            if node_name not in self.graph:
                self.graph.add_node(node_name)
                self.update_node_list()
                self.node_name_entry.delete(0, tk.END)
                self.display_error("")  # Clear previous errors
            else:
                self.display_error("Le nœud existe déjà.")
        else:
            self.display_error("Nom de nœud invalide. Utilisez seulement des lettres, chiffres, tirets et underscores.")

    def add_edge(self):
        edge_input = self.edge_nodes_entry.get()
        weight_input = self.edge_weight_entry.get()
        if edge_input and weight_input:
            nodes = edge_input.split(',')
            if len(nodes) == 2 and nodes[0] in self.graph and nodes[1] in self.graph:
                if self.validate_edge_weight(weight_input):
                    weight = float(weight_input)
                    self.graph.add_edge(nodes[0], nodes[1], weight=weight)
                    self.update_edge_list()
                    self.edge_nodes_entry.delete(0, tk.END)
                    self.edge_weight_entry.delete(0, tk.END)
                    self.display_error("")  # Clear previous errors
                else:
                    self.display_error("Le poids doit être un nombre valide et positif.")
            else:
                self.display_error("Les nœuds doivent exister dans le graphe.")
        else:
            self.display_error("Veuillez remplir tous les champs.")

    def modify_node(self):
        selected_node = self.nodes_listbox.curselection()
        if selected_node:
            node_name = self.nodes_listbox.get(selected_node)
            new_name = simpledialog.askstring("Modifier Nœud", f"Entrez un nouveau nom pour le nœud '{node_name}':")
            if new_name and new_name != node_name:
                if self.validate_node_name(new_name):
                    self.graph = nx.relabel_nodes(self.graph, {node_name: new_name})
                    self.update_node_list()
                    self.display_error("")  # Clear previous errors
                else:
                    self.display_error("Nom de nœud invalide. Utilisez seulement des lettres, chiffres, tirets et underscores.")
            else:
                self.display_error("Nom de nœud invalide.")
        else:
            self.display_error("Sélectionnez un nœud à modifier.")

    def modify_edge(self):
        selected_edge = self.edges_listbox.curselection()
        if selected_edge:
            edge_data = self.edges_listbox.get(selected_edge)
            nodes, weight = edge_data.split(" : ")
            node1, node2 = nodes.split(" - ")
            new_weight = simpledialog.askfloat("Modifier Arête", f"Entrez un nouveau poids pour l'arête {node1}-{node2} :", minvalue=0)
            if new_weight is not None:
                self.graph[node1][node2]['weight'] = new_weight
                self.update_edge_list()
                self.display_error("")  # Clear previous errors
        else:
            self.display_error("Sélectionnez une arête à modifier.")

    def delete_node(self):
        selected_node = self.nodes_listbox.curselection()
        if selected_node:
            node_name = self.nodes_listbox.get(selected_node)
            self.graph.remove_node(node_name)
            self.update_node_list()
            self.update_edge_list()
            self.display_error("")  # Clear previous errors
        else:
            self.display_error("Sélectionnez un nœud à supprimer.")

    def delete_edge(self):
        selected_edge = self.edges_listbox.curselection()
        if selected_edge:
            edge_data = self.edges_listbox.get(selected_edge)
            nodes, _ = edge_data.split(" : ")
            node1, node2 = nodes.split(" - ")
            self.graph.remove_edge(node1, node2)
            self.update_edge_list()
            self.display_error("")  # Clear previous errors
        else:
            self.display_error("Sélectionnez une arête à supprimer.")

    def update_node_list(self):
        self.nodes_listbox.delete(0, tk.END)
        for node in self.graph.nodes:
            self.nodes_listbox.insert(tk.END, node)

        # Mettre à jour les combobox avec les nœuds
        self.start_node_combobox['values'] = list(self.graph.nodes)
        self.end_node_combobox['values'] = list(self.graph.nodes)

    def update_edge_list(self):
        self.edges_listbox.delete(0, tk.END)
        for edge in self.graph.edges(data=True):
            edge_display = f"{edge[0]} - {edge[1]} : {edge[2]['weight']}"
            self.edges_listbox.insert(tk.END, edge_display)

    def load_graph(self):
        file_path = filedialog.askopenfilename(filetypes=[("Fichiers CSV", "*.csv")])
        if file_path:
            with open(file_path, mode='r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) == 1:  # Ajouter un nœud
                        self.graph.add_node(row[0])
                    elif len(row) == 3:  # Ajouter une arête
                        self.graph.add_edge(row[0], row[1], weight=float(row[2]))
            self.update_node_list()
            self.update_edge_list()

    def save_graph(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Fichiers CSV", "*.csv")])
        if file_path:
            with open(file_path, mode='w') as file:
                writer = csv.writer(file)
                for node in self.graph.nodes:
                    writer.writerow([node])
                for edge in self.graph.edges(data=True):
                    writer.writerow([edge[0], edge[1], edge[2]['weight']])

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphEditor(root)
    root.mainloop()
