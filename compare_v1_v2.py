import subprocess, os, sys
import matplotlib.pyplot as plt
from tqdm import tqdm

N_MAX = 32

def sanitize(x):
    return x.decode('utf-8').replace('\n', '').replace('\r', '')

for n in tqdm(range(1, N_MAX+1), bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'):
    output1 = sanitize(subprocess.check_output([sys.executable, 'warehouse_1.py', '-n', str(n), '-p']))
    if output1 == "Infeasible":
        plt.plot(n, float('inf'), 'ro')
    else:
        plt.plot(n, float(output1), 'ro')

    output2 = sanitize(subprocess.check_output([sys.executable, 'warehouse_2.py', '-n', str(n), '-p']))
    if output2 == "Infeasible":
        plt.plot(n, float('inf'), 'bo')
    else:
        plt.plot(n, float(output2), 'bo')

plt.title('Max Delivery Distance vs Number of Warehouses')
plt.legend(['Without Demand and Supply Constraints', 'With Demand and Supply Constraints'])
plt.xlabel('Number of Warehouses')
plt.ylabel('Max Delivery Distance')
plt.xticks(range(1, N_MAX+1, 5))
plt.savefig('./Plots/compare_v1_v2.png')
plt.show()