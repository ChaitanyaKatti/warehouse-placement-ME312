# This code adds demand and supply constraints

# Objective function: Minimize the maximum delivery time
# Decision variable: An array representing the indices of the warehouses which supply the cities
    # [0, 1, 1, 0, 1] means that the warehouses exit at 0, 1. 
    # City 0 is supplied by warehouse 0
    # 1 by 1
    # 2 by 1
    # 3 by 0
    # 4 by 1

# Each wharehouse has a particular supply limit
# Every city has a particular demand
# Each wharehouse must meet the demand of the cities it serves
# The wharehouse placement is still optimized to minimize the maximum delivery time

import numpy as np
from pymoo.core.problem import ElementwiseProblem
from pymoo.core.mixed import MixedVariableGA
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.operators.sampling.rnd import BinaryRandomSampling
from pymoo.termination.max_gen import MaximumGenerationTermination
from pymoo.termination.default import DefaultSingleObjectiveTermination
from pymoo.optimize import minimize
from utils import readDistances, readCityNames, readDemand, readSupply, plotMapPymoo
from pymoo.core.variable import Binary, Integer

import matplotlib.pyplot as plt
import geopandas as gpd

# Define the warehouse placement problem as a pymoo problem
class WarehousePlacement(ElementwiseProblem):
    def __init__(self, cities, distances, supply, demand, n_warehouses):
        self.cities = cities
        self.n_cities = len(cities)
        self.distances = distances
        self.n_warehouses = n_warehouses
        self.supply = supply
        self.demand = demand
        
        vars = {
            f"w_{i}": Integer(bounds=(0, self.n_cities-1)) for i in range(self.n_warehouses)
        }
        super().__init__(vars=vars, n_obj=1, n_eq_constr=0, n_ieq_constr=self.n_warehouses)

    def _evaluate(self, X, out, *args, **kwargs):
        max_delivery_distance = 0

        # Supply of each wharehouse
        supply = np.array([self.supply[self.cities[i]] for i in X.values()])
        demand = np.zeros(self.n_warehouses)
        
        # Loop through each city, find its nearest wharehouse and stack up the demand into that wharehouse
        for i in range(self.n_cities):
            min_distance = np.inf
            for j in range(self.n_warehouses):
                distance = self.distances[self.cities[i]][self.cities[X[f"w_{j}"]]]
                if distance < min_distance:
                    min_distance = distance
                    min_index = j
            max_delivery_distance = max(max_delivery_distance, min_distance)
            # Subtract the demand from the supply
            demand[min_index] += self.demand[self.cities[i]]
        
        # Objective: Minimize the maximum delivery time
        out["F"] = max_delivery_distance
        
        # Constraint: Each wharehouse must meet the demand of the cities it serves
        out["G"] = demand - supply # demand - supply <= 0
                    
# Dictionary to store distances
distances = readDistances('./Rajasthan/distances.csv')
cities = readCityNames('./Rajasthan/distances.csv')
supply = readSupply('./Rajasthan/supply.csv')
demand = readDemand('./Rajasthan/demand.csv')

# Create the problem instance
problem = WarehousePlacement(cities, distances, supply, demand, n_warehouses=7)

# Configure the genetic algorithm
algorithm = MixedVariableGA(pop_size=100)
termination = DefaultSingleObjectiveTermination(
    xtol=1e-8,
    cvtol=1e-6,
    ftol=1e-6,
    period=1000,
    n_max_gen=100000,
    n_max_evals=1000000
)

# Perform optimization
res = minimize(problem,
               algorithm,
               termination,
               verbose=True,
               seed=42,
               save_history=True)

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

# Plot the avg f over iterations
plt.plot([algo.pop.get("F").mean() for algo in res.history])
plt.xlabel("Iterations")
plt.ylabel("Max Delivery Time")
plt.title("Max Delivery Time Over Iterations (Genetic Algorithm, population=100)")

# Plot the results
plotMapPymoo(cities, supplier, distances, max_delivery_distance, "Warehouse Placement in Rajasthan with Demand and Supply Constraints Using Genetic Algorithms", './Rajasthan/rajasthan_district.shp')