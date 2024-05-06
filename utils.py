import csv
import geopandas as gpd
import matplotlib.pyplot as plt
import datetime

def readDistances(filename):
    # Initialize the dictionary to store distances
    distances = {}
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            start_city = row['start_city']
            end_city = row['end_city']
            distance = float(row['distance_km'])

            # Initialize distances for start_city if not already present
            if start_city not in distances:
                distances[start_city] = {}
            # Initialize distances for end_city if not already present
            if end_city not in distances:
                distances[end_city] = {}

            # Assign distance for both directions
            distances[start_city][end_city] = distance
            distances[end_city][start_city] = distance
            distances[start_city][start_city] = 0
            distances[end_city][end_city] = 0
        
    return distances

def readCityNames(filename):
    city_names = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            start_city = row['start_city']
            end_city = row['end_city']

            if start_city not in city_names:
                city_names.append(start_city)
            if end_city not in city_names:
                city_names.append(end_city)

    return city_names

def readSupply(filename):
    supply = {}
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            city = row['city']
            s = float(row['supply'])
            supply[city] = s

    return supply

def readDemand(filename):
    demand = {}
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            city = row['city']
            mean_demand = float(row['mean_demand'])
            # variance_demand = float(row['variance_demand'])
            demand[city] = mean_demand

    return demand

def readCost(filename):
    fixedCost = {}
    scalingCost = {}
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            city = row['city']
            fixedCost[city] = float(row['fixed_cost'])
            scalingCost[city] = float(row['scaling_cost'])
        
    return fixedCost, scalingCost

def plotMap(cities, supplier, distances, obj, title, filename):
    # Load the map of Rajasthan
    map = gpd.read_file(filename=filename)

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
                col = 'black'
                # See if the distance is the largest
                if abs(distances[city1][city2] - obj) < 1e-5:
                    col = 'red'

                city1_data = map[map['district'] == city1]
                city2_data = map[map['district'] == city2]
                city1_geom = city1_data.geometry.values[0]
                city2_geom = city2_data.geometry.values[0]
                plt.plot([city1_geom.centroid.x, city2_geom.centroid.x], [
                            city1_geom.centroid.y, city2_geom.centroid.y], '-', lw=1.5, alpha=0.5, color=col)

    plt.title(title)
    plt.axis('off')
    plt.text(0.5, 0.01, f"Max Delivery Distance: {obj:.2f}",
                fontsize=12, color='black',
                fontweight='bold',
                horizontalalignment='center',
                verticalalignment='center',
                transform=plt.gca().transAxes)
    plt.savefig('./Plots/' + 'plot_MILP_' + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + '.png')
    plt.show()

def plotMapPymoo(cities, supplier, distances, obj, title, filename):
    # Load the map of Rajasthan
    map = gpd.read_file(filename=filename)
        
    # Plot the map
    map.plot()

    # Plot the selected cities and warehouses
    selected_cities = [
        city for city in cities if supplier[city][city] == 1]
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
            if supplier[city1][city2] == 1:
                col = 'black'
                # See if the distance is the largest
                if abs(distances[city1][city2] - obj) < 1e-5:
                    col = 'red'

                city1_data = map[map['district'] == city1]
                city2_data = map[map['district'] == city2]
                city1_geom = city1_data.geometry.values[0]
                city2_geom = city2_data.geometry.values[0]
                plt.plot([city1_geom.centroid.x, city2_geom.centroid.x], [
                            city1_geom.centroid.y, city2_geom.centroid.y], '-', lw=1.5, alpha=0.5, color=col)

    plt.title(title)
    plt.axis('off')
    plt.text(0.5, 0.01, f"Max Delivery Distance: {obj:.2f}",
                fontsize=12, color='black',
                fontweight='bold',
                horizontalalignment='center',
                verticalalignment='center',
                transform=plt.gca().transAxes)
    # Add timestamp
    plt.savefig('./Plots/' + 'plot_GA_' + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + '.png')
    plt.show()