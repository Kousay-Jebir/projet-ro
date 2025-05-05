import gurobipy as grb
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import simpledialog
from tkinter import ttk
import networkx as nx
import csv
import re


class GurobiSolver:
    def __init__(self, graph, error_label, result_text, start_node, end_node):
        self.graph = graph
        self.error_label = error_label
        self.result_text = result_text
        self.start_node = start_node  # Nœud de départ
        self.end_node = end_node      # Nœud de destination

    def solve(self):
        if not self.graph.nodes:
            self.display_error("Le graphe est vide. Impossible de résoudre le problème.")
            return

        try:
            model = grb.Model("ShortestPath")
            model.setParam('OutputFlag', 0)  # Désactive la sortie Gurobi

            # Ajout des variables binaires pour chaque arête dirigée
            variables = {}
            for u, v in self.graph.edges:
                variables[(u, v)] = model.addVar(vtype=grb.GRB.BINARY, name=f"x_{u}_{v}")

            # Fonction objectif : minimiser la somme des poids des arêtes sélectionnées
            model.setObjective(grb.quicksum(variables[(u, v)] * self.graph[u][v]['weight'] for u, v in self.graph.edges),
                            sense=grb.GRB.MINIMIZE)

            # Contraintes de flux :
            for node in self.graph.nodes:
                inflow = grb.quicksum(variables[(u, v)] for (u, v) in self.graph.edges if v == node)
                outflow = grb.quicksum(variables[(u, v)] for (u, v) in self.graph.edges if u == node)
                if node == self.start_node:
                    model.addConstr(outflow - inflow == 1, name=f"flow_start_{node}")
                elif node == self.end_node:
                    model.addConstr(outflow - inflow == -1, name=f"flow_end_{node}")
                else:
                    model.addConstr(outflow - inflow == 0, name=f"flow_{node}")

            # Résolution
            model.optimize()

            if model.status == grb.GRB.OPTIMAL:
                result = "Solution optimale trouvée:\n"
                for (u, v) in self.graph.edges:
                    if variables[(u, v)].x > 0.5:
                        result += f"{u} -> {v} (Poids: {self.graph[u][v]['weight']})\n"
                self.result_text.config(state=tk.NORMAL)
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, result)
                self.result_text.config(state=tk.DISABLED)
            else:
                self.display_error("Aucune solution optimale trouvée.")
        except grb.GurobiError as e:
            self.display_error(f"Erreur Gurobi: {e}")
        except Exception as e:
            self.display_error(f"Une erreur est survenue: {e}")


    def display_error(self, message):
        self.error_label.config(text=message)
