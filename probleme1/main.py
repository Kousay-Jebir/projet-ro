import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import networkx as nx
import csv, re
from gurobi_solver import GurobiSolver

class GraphEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Editor")
        self.graph = nx.Graph()
        self.start_node = None
        self.end_node = None

        # Appliquer un thème ttk moderne
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabelFrame', background='#f0f0f0', borderwidth=2)
        style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('TEntry', font=('Segoe UI', 10))
        style.configure('TCombobox', font=('Segoe UI', 10))

        # Grille responsive
        self.root.geometry('900x600')
        for i in range(3): self.root.grid_columnconfigure(i, weight=1)
        for i in range(7): self.root.grid_rowconfigure(i, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(6, weight=1)

        self.create_widgets()

    def create_widgets(self):
        # Cadre ajout nœud et arête côte-à-côte
        top_frame = ttk.Frame(self.root)
        top_frame.grid(row=0, column=0, columnspan=3, sticky='ew', padx=10, pady=5)
        top_frame.grid_columnconfigure((0,1), weight=1)

        # Ajouter nœud
        node_frame = ttk.LabelFrame(top_frame, text="Ajouter un Nœud", padding=10)
        node_frame.grid(row=0, column=0, sticky='ew', padx=5)
        self.node_name_entry = ttk.Entry(node_frame)
        self.node_name_entry.grid(row=0, column=0, sticky='ew', pady=2)
        ttk.Button(node_frame, text="Ajouter", command=self.add_node).grid(row=0, column=1, padx=5)

        # Ajouter arête
        edge_frame = ttk.LabelFrame(top_frame, text="Ajouter une Arête", padding=10)
        edge_frame.grid(row=0, column=1, sticky='ew', padx=5)
        self.edge_nodes_entry = ttk.Entry(edge_frame)
        self.edge_nodes_entry.grid(row=0, column=0, sticky='ew', pady=2)
        self.edge_weight_entry = ttk.Entry(edge_frame, width=8)
        self.edge_weight_entry.grid(row=0, column=1, sticky='ew', pady=2)
        ttk.Button(edge_frame, text="Ajouter", command=self.add_edge).grid(row=0, column=2, padx=5)

        # Listes nœuds / arêtes
        list_frame = ttk.Frame(self.root)
        list_frame.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=10, pady=5)
        list_frame.grid_columnconfigure((0,1), weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        # Nœuds
        ttk.Label(list_frame, text="Nœuds").grid(row=0, column=0)
        self.nodes_listbox = tk.Listbox(list_frame, height=8)
        self.nodes_listbox.grid(row=1, column=0, sticky='nsew', padx=5)

        # Arêtes
        ttk.Label(list_frame, text="Arêtes").grid(row=0, column=1)
        self.edges_listbox = tk.Listbox(list_frame, height=8)
        self.edges_listbox.grid(row=1, column=1, sticky='nsew', padx=5)

        # Sélection départ/arrivée
        select_frame = ttk.LabelFrame(self.root, text="Plus Court Chemin", padding=10)
        select_frame.grid(row=2, column=0, columnspan=3, sticky='ew', padx=10, pady=5)
        select_frame.grid_columnconfigure((0,1,2), weight=1)
        self.start_node_combobox = ttk.Combobox(select_frame, state='readonly')
        self.start_node_combobox.set('Départ')
        self.start_node_combobox.grid(row=0, column=0, padx=5)
        self.end_node_combobox = ttk.Combobox(select_frame, state='readonly')
        self.end_node_combobox.set('Arrivée')
        self.end_node_combobox.grid(row=0, column=1, padx=5)
        ttk.Button(select_frame, text="Résoudre", command=self.solve_graph).grid(row=0, column=2, padx=5)

        # Erreur et résultat
        self.error_label = ttk.Label(self.root, text='', foreground='red')
        self.error_label.grid(row=3, column=0, columnspan=3)
        self.result_text = tk.Text(self.root, height=6, wrap=tk.WORD, state='disabled', font=('Segoe UI', 10))
        self.result_text.grid(row=4, column=0, columnspan=3, sticky='ew', padx=10, pady=5)

        # Boutons Load/Save/Modify/Delete
        btns = ['Charger', 'Sauvegarder', 'Modifier Nœud', 'Supprimer Nœud', 'Modifier Arête', 'Supprimer Arête']
        cmds = [self.load_graph, self.save_graph, self.modify_node, self.delete_node, self.modify_edge, self.delete_edge]
        for i, (t,c) in enumerate(zip(btns, cmds)):
            ttk.Button(self.root, text=t, command=c).grid(row=5 + i//3, column=i%3, sticky='ew', padx=10, pady=5)

        # Init solver
        self.solver = GurobiSolver(self.graph, self.error_label, self.result_text, self.start_node, self.end_node)

    def validate_node_name(self, node_name):
        return bool(node_name and re.match(r'^[a-zA-Z0-9_-]+$', node_name))

    def validate_edge_weight(self, weight):
        try:
            return float(weight) >= 0
        except ValueError:
            return False

    def add_node(self):
        node_name = self.node_name_entry.get()
        if self.validate_node_name(node_name):
            if node_name not in self.graph:
                self.graph.add_node(node_name)
                self.update_node_list()
                self.node_name_entry.delete(0, tk.END)
                self.display_error("")
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
                    self.display_error("")
                else:
                    self.display_error("Le poids doit être un nombre valide et positif.")
            else:
                self.display_error("Les nœuds doivent exister dans le graphe.")
        else:
            self.display_error("Veuillez remplir tous les champs.")

    def modify_node(self):
        sel = self.nodes_listbox.curselection()
        if sel:
            node = self.nodes_listbox.get(sel)
            new_name = simpledialog.askstring("Modifier Nœud", f"Nouveau nom pour '{node}':")
            if new_name and new_name != node and self.validate_node_name(new_name):
                nx.relabel_nodes(self.graph, {node: new_name}, copy=False)
                self.update_node_list()
                self.display_error("")
            else:
                self.display_error("Nom invalide ou identique.")
        else:
            self.display_error("Sélectionnez un nœud à modifier.")

    def modify_edge(self):
        sel = self.edges_listbox.curselection()
        if sel:
            data = self.edges_listbox.get(sel)
            nodes, weight = data.split(" : ")
            u,v = nodes.split(" - ")
            new_w = simpledialog.askfloat("Modifier Arête", f"Nouveau poids pour {u}-{v}:", minvalue=0)
            if new_w is not None:
                self.graph[u][v]['weight'] = new_w
                self.update_edge_list()
                self.display_error("")
        else:
            self.display_error("Sélectionnez une arête à modifier.")

    def delete_node(self):
        sel = self.nodes_listbox.curselection()
        if sel:
            node = self.nodes_listbox.get(sel)
            self.graph.remove_node(node)
            self.update_node_list()
            self.update_edge_list()
            self.display_error("")
        else:
            self.display_error("Sélectionnez un nœud à supprimer.")

    def delete_edge(self):
        sel = self.edges_listbox.curselection()
        if sel:
            data = self.edges_listbox.get(sel)
            nodes, _ = data.split(" : ")
            u,v = nodes.split(" - ")
            self.graph.remove_edge(u, v)
            self.update_edge_list()
            self.display_error("")
        else:
            self.display_error("Sélectionnez une arête à supprimer.")

    def update_node_list(self):
        self.nodes_listbox.delete(0, tk.END)
        for n in self.graph.nodes:
            self.nodes_listbox.insert(tk.END, n)
        vals = list(self.graph.nodes)
        self.start_node_combobox.configure(values=vals)
        self.end_node_combobox.configure(values=vals)

    def update_edge_list(self):
        self.edges_listbox.delete(0, tk.END)
        for u,v,d in self.graph.edges(data=True):
            self.edges_listbox.insert(tk.END, f"{u} - {v} : {d['weight']}")

    def solve_graph(self):
        start = self.start_node_combobox.get()
        end = self.end_node_combobox.get()
        if start in self.graph and end in self.graph:
            self.start_node, self.end_node = start, end
            self.solver.start_node = start
            self.solver.end_node = end
            self.solver.solve()
        else:
            self.display_error("Sélectionnez un départ et une arrivée valides.")

    def load_graph(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if path:
            with open(path) as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row)==1: self.graph.add_node(row[0])
                    elif len(row)==3: self.graph.add_edge(row[0], row[1], weight=float(row[2]))
            self.update_node_list()
            self.update_edge_list()

    def save_graph(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if path:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                for n in self.graph.nodes: writer.writerow([n])
                for u,v,d in self.graph.edges(data=True): writer.writerow([u,v,d['weight']])

    def display_error(self, message):
        self.error_label.config(text=message)

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphEditor(root)
    root.mainloop()
