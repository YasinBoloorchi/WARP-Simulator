import matplotlib.pyplot as plt

def plot_lists(lists):
    for i, data_list in enumerate(lists):
        x, y = zip(*data_list)
        y = [val + i * 0.01 for val in y]  # Adjust the y-values to separate the lines
        x = [val + i * 0.01 for val in x]  # Adjust the x-values to separate the lines
        plt.plot(x, y, marker='o', label=f'Line {i+1}')

    plt.title('Separate Lines for Each List')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.show()

# Example usage with the provided data
lists = [[(0, 0), (0, 0), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 2), (0, 2), (1, 2), (1, 2), (1, 2), (1, 2), (2, 2), (2, 2), (2, 3), (2, 3), (3, 3)] ,
[(0, 0), (0, 0), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (1, 1), (1, 1), (1, 2), (1, 2), (1, 2), (1, 2), (1, 2), (1, 2), (2, 2), (2, 2), (2, 3), (2, 3), (3, 3)] ,
[(0, 0), (0, 0), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (1, 1), (1, 1), (1, 2), (1, 2), (2, 2), (2, 2), (2, 2), (2, 2), (2, 2), (2, 2), (2, 3), (2, 3), (3, 3)] ,
[(0, 0), (0, 0), (0, 1), (0, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 2), (1, 2), (1, 2), (1, 2), (1, 2), (1, 2), (2, 2), (2, 2), (2, 3), (2, 3), (3, 3)] ,
[(0, 0), (0, 0), (0, 1), (0, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 2), (1, 2), (2, 2), (2, 2), (2, 2), (2, 2), (2, 2), (2, 2), (2, 3), (2, 3), (3, 3)]]

plot_lists(lists)
