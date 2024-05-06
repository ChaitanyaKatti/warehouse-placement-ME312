# Now varible capacity warehouse are automatically built within the given budget

# Objective function: Minimize the cost of building warehouses and operating them
# Decision variable: If a city i is supplied by a warehouse at city j
# Constraint: Each city is covered by exactly one warehouse
# Constraint: A city can supply if there exists a warehouse in that city
# Constraint: Each warehouse must meet the demand of the cities it serves

from pulp import LpProblem, LpVariable, lpSum, LpMinimize, LpSolverDefault, PULP_CBC_CMD, GUROBI_CMD
import argparse
from utils import readDistances, readCityNames, readDemand, readCost, plotMap
import geopandas as gpd
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Warehouse Placement')
    parser.add_argument('-b', '--budget', type=float,
                        default=10.0, help='Budget constraint')
    parser.add_argument('-p', '--plot', action='store_false',
                        help='Plot the warehouse placement')
    args = parser.parse_args()

    Budget = args.budget

    # Initialize the dictionary to store distances
    distances = readDistances('./Rajasthan/distances.csv')
    cities = readCityNames('./Rajasthan/distances.csv')
    demand = readDemand('./Rajasthan/demand.csv')
    fixedCost, scalingCost = readCost('./Rajasthan/cost.csv')
    cities = readCityNames('./Rajasthan/distances.csv')

    ## Create LP problem
    prob = LpProblem("Warehouse_Placement", LpMinimize)
    
    ## Design variables
    # If a city i is supplied by a warehouse at city j
    supplier = LpVariable.dicts("Supplier", (cities, cities), cat='Binary')
    # Variable capacity warehouse
    supplierCapacity = LpVariable.dicts("SupplierCapacity", (cities), cat='Continuous', lowBound=0.0)
    # Total fixed cost of building warehouses
    total_fixed_cost = lpSum((supplier[city][city] * fixedCost[city] + supplierCapacity[city] * scalingCost[city]) for city in cities)
    # Total cost of operating warehouses
    total_operating_cost = lpSum(distances[city1][city2] * demand[city1] * supplier[city1][city2] for city1 in cities for city2 in cities)

    ## Objective function: Minimize max delivery distance
    prob += total_operating_cost
    
    
    ## Constraints
    # Constraint: Budget constraint
    prob += total_fixed_cost <= Budget
    
    # Constraint: Each city is covered by exactly one warehouse
    for city1 in cities:
        prob += lpSum(supplier[city1][city2] for city2 in cities) == 1

    # Constraint: A city can supply if there exists a warehouse in that city
    for city1 in cities:
        for city2 in cities:
            prob += supplier[city1][city2] <= supplier[city2][city2]

    # Constraint: Each warehouse must meet the demand of the cities it serves
    for city2 in cities:
        prob += lpSum(supplier[city1][city2] * demand[city1]
                      for city1 in cities) <= supplierCapacity[city2]

    ## Solve the LP problem
    solver = LpSolverDefault
    prob.solve(GUROBI_CMD(msg=0))

    # Check the status of the solution
    if prob.status != 1:
        print("Infeasible")
    else:
        print("Objective: ", prob.objective.value())
        print("Fixed cost: ", total_fixed_cost.value())
        print("Operating cost: ", total_operating_cost.value())
        print("Total cost: ", total_fixed_cost.value() + total_operating_cost.value())
        print("Budget: ", Budget)
        # Print the supplier capacity
        for city in cities:
            if supplierCapacity[city].value() > 0:
                print(f"{city}: {supplierCapacity[city].value()}", supplier[city][city].value())
        
        obj = total_fixed_cost.value() + total_operating_cost.value()






    if args.plot and prob.status == 1:
        # Load the map of Rajasthan
        map = gpd.read_file(filename='./Rajasthan/rajasthan_district.shp')

        # Plot the map
        map.plot()

        # Plot the selected cities and warehouses
        selected_cities = [
            city for city in cities if supplier[city][city].value() == 1]
        for city in cities:
            city_data = map[map['district'] == city]
            city_geom = city_data.geometry.values[0]
            city_centroid = city_geom.centroid

            if city in selected_cities:
                plt.text(city_centroid.x, city_centroid.y, city, ha='center', va='bottom', fontsize=10, color='white',
                            fontweight='bold', bbox=dict(facecolor='black', alpha=0.4, boxstyle='round,pad=0.2'))
                plt.scatter(city_centroid.x, city_centroid.y,
                            color='red', marker='s', label='Warehouse')
            else:
                plt.text(city_centroid.x, city_centroid.y, city,
                            ha='center', va='bottom', fontsize=8)

        # Draw lines between warehouses and cities
        for city1 in cities:
            for city2 in cities:
                if supplier[city1][city2].value() == 1:
                    city1_data = map[map['district'] == city1]
                    city2_data = map[map['district'] == city2]
                    city1_geom = city1_data.geometry.values[0]
                    city2_geom = city2_data.geometry.values[0]
                    plt.plot([city1_geom.centroid.x, city2_geom.centroid.x], [
                                city1_geom.centroid.y, city2_geom.centroid.y], 'k-', lw=1.5, alpha=0.5)

        plt.title('Variable Capacity Warehouses\nand Budget Constraint using MILP')
        plt.axis('off')
        plt.text(0.5, 0.01, f"Total Operating Cost: {obj:.2f}",
                    fontsize=12, color='black',
                    fontweight='bold',
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=plt.gca().transAxes)
        plt.show()