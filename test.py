import z3

# List of variable names as strings
variable_names = ["F0AB", "F0BC", "F0CA"]

# Create a dictionary to store Z3 integer variables
variables = {}

# Define integer variables and store them in the dictionary
for var_name in variable_names:
    variables[var_name] = z3.Int(var_name)