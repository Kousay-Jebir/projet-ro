import gurobipy as grb
from PyQt5.QtWidgets import QMessageBox, QStatusBar, QTextEdit
import networkx as nx

class GurobiSolver:
    def __init__(self, graph, status_bar: QStatusBar, result_text: QTextEdit, start_node, end_node):
        self.graph = graph
        self.status_bar = status_bar
        self.result_text = result_text
        self.start_node = start_node  # Start node
        self.end_node = end_node      # End node

    def solve(self):
        if not self.graph.nodes:
            self.display_error("The graph is empty. Cannot solve the problem.")
            return

        try:
            model = grb.Model("ShortestPath")
            model.setParam('OutputFlag', 0)  # Disable Gurobi output

            # Add binary variables for each directed edge
            variables = {}
            for u, v in self.graph.edges:
                variables[(u, v)] = model.addVar(vtype=grb.GRB.BINARY, name=f"x_{u}_{v}")

            # Objective function: minimize total weight of selected edges
            model.setObjective(
                grb.quicksum(variables[(u, v)] * self.graph[u][v]['weight']
                            for u, v in self.graph.edges),
                sense=grb.GRB.MINIMIZE
            )

            # Flow constraints:
            for node in self.graph.nodes:
                inflow = grb.quicksum(variables[(u, v)] for (u, v) in self.graph.edges if v == node)
                outflow = grb.quicksum(variables[(u, v)] for (u, v) in self.graph.edges if u == node)

                if node == self.start_node:
                    model.addConstr(outflow - inflow == 1, name=f"flow_start_{node}")
                elif node == self.end_node:
                    model.addConstr(outflow - inflow == -1, name=f"flow_end_{node}")
                else:
                    model.addConstr(outflow - inflow == 0, name=f"flow_{node}")

            # Solve the model
            model.optimize()

            if model.status == grb.GRB.OPTIMAL:
                result = "Optimal path:\n"
                current_node = self.start_node
                path = [current_node]
                total_weight = 0

                # Trace the ordered path and collect weights of each step
                steps = []
                while current_node != self.end_node:
                    for (u, v) in self.graph.edges:
                        if u == current_node and variables[(u, v)].x > 0.5:
                            step_weight = self.graph[u][v]['weight']
                            total_weight += step_weight
                            path.append(v)
                            steps.append(f"{u} → {v} (Weight: {step_weight})")
                            current_node = v
                            break

                # Format the result
                path_str = " → ".join(str(node) for node in path)
                step_details = "\n".join(steps)
                result += f"Path: {path_str}\nSteps:\n{step_details}\nTotal weight: {total_weight}"
                self.result_text.setPlainText(result)
                self.status_bar.showMessage("Solution found successfully!", 3000)
            else:
                self.display_error("No optimal solution found.")

        except grb.GurobiError as e:
            self.display_error(f"Gurobi error: {e}")
        except Exception as e:
            self.display_error(f"An error occurred: {e}")

    def display_error(self, message):
        """Display error message in status bar and show a message box"""
        self.status_bar.showMessage(message, 5000)  # Show for 5 seconds
        self.show_message("Error", message)

    def show_message(self, title, message):
        """Show a modal error message dialog"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("QLabel{color: black;} QMessageBox{background-color: white;}")
        msg.exec_()
