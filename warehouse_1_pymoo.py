# This only features worst delivery time minimization

# Objective function: Minimize the maximum delivery time
# Decision variable: An array representing the indices of the warehouses

import numpy as np
from pymoo.core.problem import ElementwiseProblem
from pymoo.core.mixed import MixedVariableGA
from pymoo.termination.default import DefaultSingleObjectiveTermination
from pymoo.optimize import minimize
from utils import readDistances, readCityNames, plotMapPymoo
from pymoo.core.variable import Integer

import matplotlib.pyplot as plt
import geopandas as gpd

# Define the warehouse placement problem as a pymoo problem
class WarehousePlacement(ElementwiseProblem):
    def __init__(self, cities, distances, n_warehouses):
        self.cities = cities
        self.n_cities = len(cities)
        self.distances = distances
        self.n_warehouses = n_warehouses
        vars = {
            f"w_{i}": Integer(bounds=(0, self.n_cities-1)) for i in range(self.n_warehouses)
        }
        super().__init__(vars=vars, n_obj=1, n_eq_constr=0, n_ieq_constr=0)

    def _evaluate(self, X, out, *args, **kwargs):
        max_delivery_distance = 0
        
        for i in range(self.n_cities):
            min_distance = np.inf
            for j in range(self.n_warehouses):
                distance = self.distances[self.cities[i]][self.cities[X[f"w_{j}"]]]
                if distance < min_distance:
                    min_distance = distance
            max_delivery_distance = max(max_delivery_distance, min_distance)
        
        # Objective: Minimize the maximum delivery time
        out["F"] = max_delivery_distance

# Dictionary to store distances
distances = readDistances('./Rajasthan/distances.csv')
cities = readCityNames('./Rajasthan/distances.csv')

# Create the problem instance
problem = WarehousePlacement(cities, distances, n_warehouses=5)

# Configure the genetic algorithm
algorithm = MixedVariableGA(pop_size=100)
termination = DefaultSingleObjectiveTermination(
    xtol=1e-8,
    cvtol=1e-6,
    ftol=1e-6,
    period=100,
    n_max_gen=10000000,
    n_max_evals=10000000
)

# Perform optimization
res = minimize(problem,
               algorithm,
               termination,
               verbose=True,
               seed=1)

# Get the results
best_solution = res.X
max_delivery_distance = np.min(res.F)

# A array cities where the warehouses are placed
wharehouses = [cities[best_solution[f"w_{i}"]] for i in range(problem.n_warehouses)]
print(wharehouses)

# Create the adjacency matrix
supplier = {
    city1: {
        city2: 0 for city2 in cities
    }
    for city1 in cities
}
for city1 in cities:
    min_index = np.argmin([distances[city1][city2] for city2 in wharehouses])
    supplier[city1][wharehouses[min_index]] = 1

# Plot the results
plotMapPymoo(cities, supplier, distances, max_delivery_distance, "Warehouse Placement", './Rajasthan/rajasthan_district.shp')