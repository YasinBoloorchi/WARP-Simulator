import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def plot_arrival_curve_3D(data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Extract x, y, and z values from the data
    x_values = [entry[0] for entry in data]
    y_values = [entry[1] for entry in data]
    z_values = [entry[2] for entry in data]

    # Create a mapping of unique y_values to numerical indices
    y_unique = list(y_values)
    y_indices = [y_unique.index(y) for y in y_values]
    
    ax.plot(x_values, y_indices, z_values, marker='o', color='r', linestyle='-', markersize=8)

    ax.set_xticks(np.arange(min(x_values), max(x_values)+1, 1))
    ax.set_yticks(np.arange(min(y_indices), max(y_indices)+1, 1))
    ax.set_zticks(np.arange(min(z_values), max(z_values)+1, 1))
    ax.set_yticklabels(y_values)  # Set tick labels to the actual y_values

    ax.set_xlabel('Time model')
    ax.set_ylabel('Time')
    ax.set_zlabel('Packet Released')

    plt.show()

# Example usage with your provided data
data = [(0, "t", 1), (3, "t + 1", 2), (0, "t + 2", 2), (3, "t + 3", 2), (0, "t + 4", 3), (3, "t + 5", 3), (0, "t + 6", 3)]
plot_arrival_curve_3D(data)
