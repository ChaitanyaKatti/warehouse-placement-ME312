import csv
import numpy as np
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.operators.sampling.rnd import BinaryRandomSampling
from pymoo.termination.max_gen import MaximumGenerationTermination

class WarehousePlacement(Problem):
    def _init_(self):
        super()._init_(n_var=len(cities), n_obj=3, n_constr=0, xl=0, xu=1, type_var=np.int)

    def _evaluate(self, X, out, *args, **kwargs):
        total_time = np.sum([distances[cities[i]][cities[j]] * X[:, i]
                            for i in range(len(cities)) for j in range(len(cities)) if i != j], axis=1)
        total_fixed_cost = np.sum(
            [(land_cost[cities[i]] + construction_cost[cities[i]]) * X[:, i] for i in range(len(cities))], axis=1)
        total_ease_of_business = np.sum(
            [ease_of_business[cities[i]] * X[:, i] for i in range(len(cities))], axis=1)

        # Calculate penalty for understocking
        penalty = np.sum([np.max(0, demand[cities[i]] - np.sum(X[:, i]) /
                         supply[cities[i]]) for i in range(len(cities))])

        # Adjust the objective function to penalize understocking
        out["F"] = np.column_stack(
            [total_time, total_fixed_cost, total_ease_of_business + penalty])


# Read CSV files and extract data
cities = []
distances = {}
land_cost = {}
construction_cost = {}
ease_of_business = {}
demand = {}
supply = {}
with open('./Rajasthan/city_distances.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        start_city = row['start_city']
        end_city = row['end_city']
        distance = float(row['distance_km'])

        if start_city not in cities:
            cities.append(start_city)
        if end_city not in cities:
            cities.append(end_city)

        if start_city not in distances:
            distances[start_city] = {}
        if end_city not in distances:
            distances[end_city] = {}

        distances[start_city][end_city] = distance
        distances[end_city][start_city] = distance

with open('./Rajasthan/cost.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        city = row['city']
        l_cost = float(row['fixed_cost'])
        con_cost = float(row['construction_cost'])
        eob = float(row['ease_of_business'])

        land_cost[city] = l_cost
        construction_cost[city] = con_cost
        ease_of_business[city] = eob

with open('./Rajasthan/demand.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        city = row['city']
        mean_demand = float(row['mean_demand'])
        variance_demand = float(row['variance_demand'])

        # Assume demand follows a normal distribution
        demand[city] = mean_demand + \
            np.random.normal(0, np.sqrt(variance_demand))

with open('./Rajasthan/supply.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        city = row['city']
        s = float(row['supply'])
        supply[city] = s

# Create and run the optimization problem
problem = WarehousePlacement()
algorithm = NSGA2(
    pop_size=100,
    sampling=BinaryRandomSampling(),
    crossover=TwoPointCrossover(),
    mutation=BitflipMutation(),
    eliminate_duplicates=True
)
termination = MaximumGenerationTermination(200)
res = minimize(problem, algorithm, termination, seed=1)

# Print the results
for solution in res.X:
    print(solution)
