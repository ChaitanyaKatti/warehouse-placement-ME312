# This only features worst delivery time minimization

# Objective function: Minimize the maximum delivery time
# Decision variable: If a city i is supplied by a warehouse at city j
# Constraint: Total delivery time for each city
# Constraint: Each city is covered by exactly one warehouse
# Constraint: Number of warehouses
# Constraint: A city can supply if there exists a warehouse in that city

from pulp import LpProblem, LpVariable, lpSum, LpMinimize, LpSolverDefault, PULP_CBC_CMD, GUROBI_CMD
import argparse
from utils import readDistances, readCityNames, plotMap

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Warehouse Placement')
    parser.add_argument('-n', '--number', type=int,
                        default=3, help='Number of warehouses')
    parser.add_argument('-p', '--plot', action='store_false',
                        help='Plot the warehouse placement')
    args = parser.parse_args()

    if args.number < 1:
        print("Number of warehouses should be at least 1")
        exit(1)
    N = args.number

    # Dctionary to store distances
    distances = readDistances('./Rajasthan/distances.csv')
    cities = readCityNames('./Rajasthan/distances.csv')

    # Create LP problem
    prob = LpProblem("Warehouse_Placement", LpMinimize)

    # Define variable for total delivery time
    max_distance = LpVariable("Max_Distance", lowBound=0, cat='Continuous')

    # Objective function: Minimize max delivery distance
    prob += max_distance

    # Decision variable: If a city i is supplied by a warehouse at city j
    supplier = LpVariable.dicts("Supplier", (cities, cities), cat='Binary')

    # Constraint: Max delivery distance of a city from the supplier
    # prob += max_distance == lpSum(distances[city1][city2] * supplier[city1][city2] for city1 in cities for city2 in cities)
    for city1 in cities:
        for city2 in cities:
            prob += max_distance >= distances[city1][city2] * supplier[city1][city2]

    # Constraint: Each city is covered by exactly one warehouse
    for city1 in cities:
        prob += lpSum(supplier[city1][city2] for city2 in cities) == 1

    # # Decision varible: If a city is a warehouse
    # unique_supplier = LpVariable.dict("unique_supplier", (cities), cat='Binary')
    # for city2 in cities:
    #     prob += unique_supplier[city2] <= lpSum(supplier[city1][city2] for city1 in cities)
    #     prob += unique_supplier[city2] >= lpSum(supplier[city1][city2] for city1 in cities) / (len(cities) + 1)

    # # Constraint: Number of warehouses
    # prob += lpSum(unique_supplier[city] for city in cities) == N

    # Constraint: Number of warehouses
    prob += lpSum(supplier[city][city] for city in cities) == N

    # Constraint: A city can supply if there exists a warehouse in that city
    for city1 in cities:
        for city2 in cities:
            prob += supplier[city1][city2] <= supplier[city2][city2]

    # Solve the problem
    solver = LpSolverDefault
    prob.solve(GUROBI_CMD(msg=0))
    # prob.solve(PULP_CBC_CMD(msg=0)) # Use this if you don't have Gurobi installed
    
    # Check the status of the solution
    if prob.status != 1:
        print("Infeasible")
    else:
        print(prob.objective.value())

    if args.plot and prob.status == 1:
        plotMap(cities, supplier, distances, prob.objective.value(), "Warehouse Placement using MLP", './Rajasthan/rajasthan_district.shp')