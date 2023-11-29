import matplotlib.pyplot as plt

data = [(1, 1), (2, 1), (3, 2), (4, 2), (5, 3), (6, 3)]

x_values, y_values = zip(*data)

plt.step(x_values, y_values, where='mid')  # Change 'post' to 'mid'
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Step Function (Continuous from Left)')
plt.show()
