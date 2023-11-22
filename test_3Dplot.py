import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from sympy import symbols
    
def plot_3d_data(data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Extract x, y, and z values from the data
    x_values = [entry[0] for entry in data]
    y_values = [entry[1] for entry in data]
    z_values = [entry[2] for entry in data]

    # Convert x_values to numerical indices for categorical plotting
    y_indices = np.arange(len(y_values))

    ax.plot(x_values, y_indices, z_values, marker='o', color='r', linestyle='-', markersize=8)

    ax.set_xticks(np.arange(min(x_values), max(x_values)+1, 3))
    ax.set_yticks(np.arange(min(y_indices), max(y_indices)+1, 1))
    ax.set_yticklabels(y_indices)

    ax.set_xlabel('Time model')
    ax.set_ylabel('Time')
    ax.set_zlabel('Packet Released')

    plt.show()

t = symbols('t')
# Example usage with your provided data
data = [(0, "t", 1), (3, "t + 1", 2), (0, "t + 2", 2), (3, "t + 3", 2), (0, "t + 4", 3), (3, "t + 5", 3), (0, "t + 6", 3)] # Assuming 't', 't+1', 't+2' are string values
plot_3d_data(data)
