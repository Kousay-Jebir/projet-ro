import gurobipy as grb
import tkinter as tk

class ResourceSolver:
    def __init__(self, costs, constraints, error_label, result_text, demand=None):
        self.costs = costs
        self.constraints = constraints
        self.error_label = error_label
        self.result_text = result_text
        self.demand = demand
    
    def solve(self):
        if not self.costs or not self.constraints:
            self.display_error("Invalid input data.")
            return
        
        # Validate constraints before solving
        for a_ij, b_j in self.constraints:
            if len(a_ij) != len(self.costs):
                self.display_error(f"Constraint {a_ij} has wrong length. Expected {len(self.costs)} values.")
                return
        
        try:
            model = grb.Model("ResourceAllocation")
            model.setParam('OutputFlag', 0)
            
            # Variables: x_i >= 0
            activities = range(len(self.costs))
            x = [model.addVar(lb=0, name=f"x_{i}") for i in activities]
            
            # Add demand constraint if specified
            if self.demand is not None and self.demand > 0:
                model.addConstr(
                    grb.quicksum(x[i] for i in activities) >= self.demand,
                    name="demand"
                )
            
            # Objective: Minimize total cost
            model.setObjective(
                grb.quicksum(self.costs[i] * x[i] for i in activities),
                sense=grb.GRB.MINIMIZE
            )
            
            # Constraints
            for j, (a_ij, b_j) in enumerate(self.constraints):
                model.addConstr(
                    grb.quicksum(a_ij[i] * x[i] for i in activities) <= b_j,
                    name=f"constr_{j}"
                )
            
            # Optimize the model
            model.optimize()
            
            # Handle different solution statuses
            if model.status == grb.GRB.OPTIMAL:
                result = "Optimal Solution:\n"
                for i in activities:
                    if x[i].x > 1e-6:  # Only show non-zero activities (with small tolerance)
                        result += f"Activity {i}: {x[i].x:.2f}\n"
                    else:
                        result += f"Activity {i}: 0.00\n"
                result += f"\nTotal Cost: {model.objVal:.2f}"
                self.display_result(result)
                self.display_error("")  
            elif model.status == grb.GRB.INFEASIBLE:
                self.display_error("No feasible solution exists. Try relaxing some constraints.")
                try:
                    model.computeIIS()
                    iis_constraints = [c.constrName for c in model.getConstrs() if c.IISConstr]
                    iis_message = f"Conflicting constraints: {', '.join(iis_constraints)}"
                    self.display_result(f"The problem is infeasible.\n\n{iis_message}")
                except:
                    self.display_result("The problem is infeasible. No solution exists.")
            elif model.status == grb.GRB.UNBOUNDED:
                self.display_error("The problem is unbounded. No finite optimal solution exists.")
                self.display_result("The problem is unbounded, which means resources can be allocated "
                                  "without limit, resulting in an infinitely negative cost.")
            else:
                self.display_error(f"Unexpected solution status: {model.status}")
                self.display_result("The solver could not find a solution. Please check your inputs.")
                
        except grb.GurobiError as e:
            self.display_error(f"Solver error: {e}")
            self.display_result("An error occurred while solving the problem. Check your inputs.")
        except Exception as e:
            self.display_error(f"Unexpected error: {e}")
            self.display_result("An unexpected error occurred. Please check your inputs and try again.")
    
    def display_result(self, message):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, message)
        self.result_text.config(state=tk.DISABLED)
    
    def display_error(self, message):
        self.error_label.config(text=message)
