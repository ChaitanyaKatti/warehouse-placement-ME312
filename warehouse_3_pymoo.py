# This code adds bugdet constraints to the warehouse placement problem
# Each warehouse has a particular budget consideration, based on land cost, construction cost, etc.
# The total cost of all the warehouses combined must not exceed a certain limit
# The warehouse placement is still optimized to minimize the maximum delivery time
# However we are free to choose the number of warehouses, as long as the budget constraint is satisfied

# Objective function: Minimize the maximum delivery time
# Decision variable: An array of binary variables representing if a warehouse exists in a city

# Each warehouse has a particular supply limit
# Every city has a particular demand
# Each warehouse must meet the demand of the cities it serves
# The warehouse placement is still optimized to minimize the maximum delivery time

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
from utils import readDistances, readCityNames, readDemand, readSupply, readCost, plotMapPymoo
from pymoo.core.variable import Binary, Integer

import matplotlib.pyplot as plt
import geopandas as gpd

# Define the warehouse placement problem as a pymoo problem
class WarehousePlacement(ElementwiseProblem):
    def __init__(self, cities, distances, supply, demand, fixedCost, budget):
        self.cities = cities
        self.distances = distances
        self.supply = supply
        self.demand = demand
        self.fixedCost = fixedCost
        self.budget = budget
        self.n_cities = len(cities)
        
        # Decision variables: Binary array representing if a warehouse exists in a city
        vars = {
            f"x_{i}": Binary() for i in range(self.n_cities)
        }
        super().__init__(vars=vars, n_obj=1, n_eq_constr=0, n_ieq_constr=1+self.n_cities)

    def _evaluate(self, X, out, *args, **kwargs):
        max_delivery_distance = 0
        
        total_demand = {city: 0 for city in self.cities} # total demand expected by each warehouse
        
        # Loop through each city, find its nearest warehouse and stack up the demand into that warehouse
        for i in range(self.n_cities):
            min_distance = np.inf
            min_index = 0
            for j in range(self.n_cities):
                if X[f"x_{j}"] == 1:
                    distance = self.distances[self.cities[i]][self.cities[j]]
                    if distance < min_distance:
                        min_distance = distance
                        min_index = j
            max_delivery_distance = max(max_delivery_distance, min_distance)
            total_demand[self.cities[min_index]] += self.demand[self.cities[i]]
        
        total_cost = np.sum([self.fixedCost[self.cities[i]] for i in range(self.n_cities) if X[f"x_{i}"] == 1])
        
        # Objective: Minimize the maximum delivery time
        out["F"] = max_delivery_distance
        
        # Constraint: Each warehouse must meet the demand of the cities it serves
        out["G"] = np.row_stack([
            total_demand[self.cities[i]] - self.supply[self.cities[i]] for i in range(self.n_cities) # Demand <= Supply
        ]
        +
        [
            total_cost - self.budget # Total cost <= Budget
        ])
                    
# Dictionary to store distances
distances = readDistances('./Rajasthan/distances.csv')
cities = readCityNames('./Rajasthan/distances.csv')
supply = readSupply('./Rajasthan/supply.csv')
fixedCost, _ = readCost('./Rajasthan/cost.csv')
demand = readDemand('./Rajasthan/demand.csv')

# Create the problem instance
problem = WarehousePlacement(cities, distances, supply, demand, fixedCost, budget=7)

# Configure the genetic algorithm
algorithm = MixedVariableGA(pop_size=100)
termination = DefaultSingleObjectiveTermination(
    xtol=1e-8,
    cvtol=1e-6,
    ftol=1e-6,
    period=1000,
    n_max_gen=1000,
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
warehouses = [cities[i] for i in range(len(cities)) if best_solution[f"x_{i}"] == 1]
print(warehouses)

# Create the adjacency matrix
supplier = {
    city1: {
        city2: 0 for city2 in cities
    }
    for city1 in cities
}
for city1 in cities:
    min_index = np.argmin([distances[city1][city2] for city2 in warehouses])
    supplier[city1][warehouses[min_index]] = 1

# Plot the avg f over iterations
plt.plot([algo.pop.get("F").mean() for algo in res.history])
plt.xlabel("Iterations")
plt.ylabel("Max Delivery Distance")
plt.title("Max Delivery Distance Over Iterations (Genetic Algorithm, population=100)")
plt.show()

# Plot the results
plotMapPymoo(cities, supplier, distances, max_delivery_distance, "Warehouse Placement in Rajasthan with Demand, Supply and\nBudget Constraints Using Genetic Algorithms", './Rajasthan/rajasthan_district.shp')