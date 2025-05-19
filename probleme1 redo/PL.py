import gurobipy as gp
from gurobipy import GRB

def solve_lp(variable_names, c, A, b, sense, objective_type=GRB.MINIMIZE):
    model = gp.Model("generic_lp")

    n = len(c)
    x = model.addVars(variable_names, name="x", lb=0)
    model.setObjective(gp.quicksum(c[i] * x[variable_names[i]] for i in range(n)), objective_type)

    for i in range(len(b)):
        if sense[i] == '<=':
            model.addConstr(gp.quicksum(A[i][j] * x[variable_names[j]] for j in range(n)) <= b[i], name=f"constraint_{i}")
        elif sense[i] == '>=':
            model.addConstr(gp.quicksum(A[i][j] * x[variable_names[j]] for j in range(n)) >= b[i], name=f"constraint_{i}")
        elif sense[i] == '==':
            model.addConstr(gp.quicksum(A[i][j] * x[variable_names[j]] for j in range(n)) == b[i], name=f"constraint_{i}")
        else:
            raise ValueError(f"Invalid constraint sense: {sense[i]}")

    model.optimize()

    if model.status == GRB.OPTIMAL:
        solution = {
            "objective_value": model.objVal,
            "variables": {v.varName: v.x for v in model.getVars()}
        }
    else:
        solution = {
            "objective_value": None,
            "variables": None
        }

    return solution
