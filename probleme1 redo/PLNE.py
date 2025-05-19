import gurobipy as gp
from gurobipy import GRB

def solve_knapsack(values, weights, capacity):
    model = gp.Model("Knapsack Problem")

    num_items = len(values)
    x = model.addVars(num_items, vtype=GRB.INTEGER, name="x")

    obj = gp.quicksum(values[i] * x[i] for i in range(num_items))
    model.setObjective(obj, GRB.MAXIMIZE)

    model.addConstr(gp.quicksum(weights[i] * x[i] for i in range(num_items)) <= capacity, name="Capacity")

    model.optimize()

    selected_items = {i: int(x[i].x) for i in range(num_items) if x[i].x > 0}
    total_value = sum(values[i] * selected_items[i] for i in selected_items)
    print(selected_items)
    print(total_value)
    return total_value, selected_items
