data = [(0, "t", 1), (3, "t + 1", 2), (0, "t + 2", 2), (3, "t + 3", 2), (0, "t + 4", 3), (3, "t + 5", 3), (0, "t + 6", 3)]

# Remove the first element from each tuple in the list
new_data = [entry[1:] for entry in data]

print("Original data:", data)
print("Data without the first index:", new_data)