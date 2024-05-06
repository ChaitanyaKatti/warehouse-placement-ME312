# This code adds bugdet constraints to the warehouse placement problem
# Each wharehouse has a particular budget consideration, based on land cost, construction cost, etc.
# The total cost of all the warehouses combined must not exceed a certain limit
# The wharehouse placement is still optimized to minimize the maximum delivery time
# However we are free to choose the number of warehouses, as long as the budget constraint is satisfied

# Objective function: Minimize the maximum delivery time
# Decision variable: If a city i is supplied by a warehouse at city j
# Constraint: Each city is covered by exactly one warehouse
# Constraint: Total cost < Budget
# Constraint: A city can supply if there exists a warehouse in that city
# Constraint: Each wharehouse must meet the demand of the cities it serves

from pulp import LpProblem, LpVariable, lpSum, LpMinimize, LpSolverDefault, PULP_CBC_CMD, GUROBI_CMD
import argparse
from utils import readDistances, readCityNames, readSupply, readDemand, readCost, plotMap

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Warehouse Placement')
    parser.add_argument('-b', '--budget', type=float,
                        default=10.0, help='Budget constraint')
    parser.add_argument('-p', '--plot', action='store_false',
                        help='Plot the warehouse placement')
    args = parser.parse_args()

    Budget = args.budget

    # Dictionary to store distances
    distances = readDistances('./Rajasthan/distances.csv')
    cities = readCityNames('./Rajasthan/distances.csv')
    supply = readSupply('./Rajasthan/supply.csv')
    demand = readDemand('./Rajasthan/demand.csv')
    fixedCost, _ = readCost('./Rajasthan/cost.csv')

    # Create LP problem
    prob = LpProblem("Warehouse_Placement", LpMinimize)

    # Define variable for total delivery time
    max_distance = LpVariable("Max_Distance", lowBound=0, cat='Continuous')

    # Objective function: Minimize max delivery distance
    prob += max_distance

    # Decision variable: If a city i is supplied by a warehouse at city j
    supplier = LpVariable.dicts("Supplier", (cities, cities), cat='Binary')

    # Constraint: Max delivery distance of a city from the supplier
    for city1 in cities:
        for city2 in cities:
            prob += max_distance >= distances[city1][city2] * supplier[city1][city2]

    # Constraint: Each city is covered by exactly one warehouse
    for city1 in cities:
        prob += lpSum(supplier[city1][city2] for city2 in cities) == 1

    # Constraint: Total cost < Budget
    prob += lpSum(supplier[city][city] * fixedCost[city]
                  for city in cities) <= Budget

    # Constraint: A city can supply if there exists a warehouse in that city
    for city1 in cities:
        for city2 in cities:
            prob += supplier[city1][city2] <= supplier[city2][city2]

    # Constraint: Each wharehouse must meet the demand of the cities it serves
    for city2 in cities:
        prob += lpSum(supplier[city1][city2] * demand[city1]
                      for city1 in cities) <= supply[city2] * supplier[city2][city2]

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
        plotMap(cities, supplier, distances, prob.objective.value(), "Warehouse Placement in Rajasthan with Demand, Supply and\nBudget Constraint using MLP", './Rajasthan/rajasthan_district.shp')