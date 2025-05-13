import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from resource_solver import ResourceSolver

class ResourceAllocator:
    def __init__(self, root):
        self.root = root
        self.root.title("Resource Allocation Minimizer")
        self.costs = []
        self.constraints = []  # Each constraint: (a_ij list, b_j)

        # GUI Styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Error.TLabel', foreground='red', background='#f0f0f0', font=('Segoe UI', 10, 'bold'))
        style.configure('Success.TLabel', foreground='green', background='#f0f0f0', font=('Segoe UI', 10))

        # Layout
        self.root.geometry('800x650')
        for i in range(3): self.root.grid_columnconfigure(i, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.create_widgets()

    def create_widgets(self):
        # Cost Input
        cost_frame = ttk.LabelFrame(self.root, text="Activity Costs", padding=10)
        cost_frame.grid(row=0, column=0, padx=10, pady=5, sticky='ew')
        self.cost_entry = ttk.Entry(cost_frame)
        self.cost_entry.grid(row=0, column=0, padx=5, sticky='ew')
        ttk.Button(cost_frame, text="Add Cost", command=self.add_cost).grid(row=0, column=1, padx=5)
        ttk.Button(cost_frame, text="Remove Last", command=self.remove_last_cost).grid(row=0, column=2, padx=5)

        # Constraint Input
        constraint_frame = ttk.LabelFrame(self.root, text="Constraints (a_ij, b_j)", padding=10)
        constraint_frame.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        self.a_ij_entry = ttk.Entry(constraint_frame, width=20)
        self.a_ij_entry.grid(row=0, column=0, padx=5)
        self.b_j_entry = ttk.Entry(constraint_frame, width=8)
        self.b_j_entry.grid(row=0, column=1, padx=5)
        ttk.Button(constraint_frame, text="Add Constraint", command=self.add_constraint).grid(row=0, column=2, padx=5)
        ttk.Button(constraint_frame, text="Remove Last", command=self.remove_last_constraint).grid(row=0, column=3, padx=5)

        # Demand Constraint
        demand_frame = ttk.LabelFrame(self.root, text="Minimum Total Demand", padding=10)
        demand_frame.grid(row=0, column=2, padx=10, pady=5, sticky='ew')
        self.demand_entry = ttk.Entry(demand_frame, width=8)
        self.demand_entry.grid(row=0, column=0, padx=5, sticky='ew')
        self.demand_entry.insert(0, "5.0")  # Default value

        # Lists
        list_frame = ttk.Frame(self.root)
        list_frame.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=10, pady=5)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_columnconfigure(1, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)
        
        ttk.Label(list_frame, text="Costs (c_i)").grid(row=0, column=0)
        self.costs_listbox = tk.Listbox(list_frame, width=20, height=10)
        self.costs_listbox.grid(row=1, column=0, sticky='nsew', padx=5)
        costs_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.costs_listbox.yview)
        costs_scrollbar.grid(row=1, column=0, sticky='nse')
        self.costs_listbox.configure(yscrollcommand=costs_scrollbar.set)

        ttk.Label(list_frame, text="Constraints (Sum(a_ij * x_i) <= b_j)").grid(row=0, column=1)
        self.constraints_listbox = tk.Listbox(list_frame, width=40, height=10)
        self.constraints_listbox.grid(row=1, column=1, sticky='nsew', padx=5)
        constraints_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.constraints_listbox.yview)
        constraints_scrollbar.grid(row=1, column=1, sticky='nse')
        self.constraints_listbox.configure(yscrollcommand=constraints_scrollbar.set)

        # Control buttons
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        ttk.Button(button_frame, text="Solve", command=self.solve).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Clear All", command=self.clear_all).grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="Load Data", command=self.load_data).grid(row=0, column=2, padx=10)
        ttk.Button(button_frame, text="Save Data", command=self.save_data).grid(row=0, column=3, padx=10)

        # Status and Results
        self.error_label = ttk.Label(self.root, text="", style='Error.TLabel')
        self.error_label.grid(row=3, column=0, columnspan=3, pady=5)
        
        result_frame = ttk.LabelFrame(self.root, text="Solution Results", padding=10)
        result_frame.grid(row=4, column=0, columnspan=3, sticky='nsew', padx=10, pady=5)
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_rowconfigure(0, weight=1)
        
        self.result_text = tk.Text(result_frame, height=10, wrap=tk.WORD, state='disabled')
        self.result_text.grid(row=0, column=0, sticky='nsew')
        result_scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        result_scrollbar.grid(row=0, column=0, sticky='nse')
        self.result_text.configure(yscrollcommand=result_scrollbar.set)

    def add_cost(self):
        try:
            cost = float(self.cost_entry.get())
            self.costs.append(cost)
            self.costs_listbox.insert(tk.END, f"c_{len(self.costs)-1}: {cost:.2f}")
            self.cost_entry.delete(0, tk.END)
            self.error_label.config(text="")
        except ValueError:
            self.error_label.config(text="Invalid cost value. Please enter a number.")

    def remove_last_cost(self):
        if self.costs:
            self.costs.pop()
            self.costs_listbox.delete(tk.END)
            self.error_label.config(text="")
        else:
            self.error_label.config(text="No costs to remove.")

    def add_constraint(self):
        try:
            a_ij_text = self.a_ij_entry.get().strip()
            
            # Support different input formats (comma-separated or space-separated)
            if ',' in a_ij_text:
                a_ij = [float(x.strip()) for x in a_ij_text.split(',')]
            else:
                a_ij = [float(x) for x in a_ij_text.split()]
                
            b_j = float(self.b_j_entry.get())
            
            if not self.costs:
                self.error_label.config(text="Add costs first before adding constraints.")
                return
                
            if len(a_ij) != len(self.costs):
                self.error_label.config(text=f"Expected {len(self.costs)} a_ij values, got {len(a_ij)}.")
                return
                
            self.constraints.append((a_ij, b_j))
            self.constraints_listbox.insert(tk.END, f"{a_ij} <= {b_j:.2f}")
            self.a_ij_entry.delete(0, tk.END)
            self.b_j_entry.delete(0, tk.END)
            self.error_label.config(text="")
        except ValueError:
            self.error_label.config(text="Invalid constraint values. Check format and try again.")

    def remove_last_constraint(self):
        if self.constraints:
            self.constraints.pop()
            self.constraints_listbox.delete(tk.END)
            self.error_label.config(text="")
        else:
            self.error_label.config(text="No constraints to remove.")

    def solve(self):
        if not self.costs:
            self.error_label.config(text="Add costs before solving.")
            return
            
        if not self.constraints:
            self.error_label.config(text="Add at least one constraint before solving.")
            return
        
        try:
            demand = float(self.demand_entry.get()) if self.demand_entry.get().strip() else None
            
            # Validate demand is positive if provided
            if demand is not None and demand <= 0:
                self.error_label.config(text="Demand must be greater than zero.")
                return
                
            solver = ResourceSolver(self.costs, self.constraints, self.error_label, self.result_text, demand)
            solver.solve()
        except ValueError:
            self.error_label.config(text="Invalid demand value. Please enter a number.")

    def clear_all(self):
        self.costs = []
        self.constraints = []
        self.costs_listbox.delete(0, tk.END)
        self.constraints_listbox.delete(0, tk.END)
        self.error_label.config(text="")
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)

    def load_data(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("All Files", "*.*")])
        if not path:
            return
            
        try:
            with open(path, 'r') as f:
                reader = csv.reader(f)
                # First row should be costs
                try:
                    self.costs = list(map(float, next(reader)))
                except StopIteration:
                    self.error_label.config(text="Empty CSV file.")
                    return
                except ValueError:
                    self.error_label.config(text="Invalid cost values in CSV.")
                    return
                    
                # Remaining rows are constraints
                self.constraints = []
                for row in reader:
                    if not row:
                        continue
                    try:
                        a_ij = list(map(float, row[:-1]))
                        b_j = float(row[-1])
                        
                        # Validate constraint length
                        if len(a_ij) != len(self.costs):
                            self.error_label.config(text=f"Constraint in CSV has wrong length: expected {len(self.costs)}, got {len(a_ij)}.")
                            self.costs = []
                            self.constraints = []
                            return
                            
                        self.constraints.append((a_ij, b_j))
                    except ValueError:
                        self.error_label.config(text="Invalid constraint values in CSV.")
                        self.costs = []
                        self.constraints = []
                        return
                        
            self.update_lists()
            self.error_label.config(text="")
            
        except Exception as e:
            self.error_label.config(text=f"Error loading file: {str(e)}")

    def save_data(self):
        if not self.costs:
            self.error_label.config(text="No data to save.")
            return
            
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
            
        try:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.costs)
                for a_ij, b_j in self.constraints:
                    writer.writerow(a_ij + [b_j])
            self.error_label.config(text="")
        except Exception as e:
            self.error_label.config(text=f"Error saving file: {str(e)}")

    def update_lists(self):
        self.costs_listbox.delete(0, tk.END)
        for i, cost in enumerate(self.costs):
            self.costs_listbox.insert(tk.END, f"c_{i}: {cost:.2f}")
        self.constraints_listbox.delete(0, tk.END)
        for a_ij, b_j in self.constraints:
            self.constraints_listbox.insert(tk.END, f"{a_ij} <= {b_j:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ResourceAllocator(root)
    root.mainloop()
