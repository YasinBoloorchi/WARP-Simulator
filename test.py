import sympy

# Convert an integer to a SymPy expression
x = sympy.Integer(5)
y = sympy.symbols('S')
# Perform symbolic manipulation on the expression
# expr = x ** 2 + 3 * x + 2


# Substitute a value into the expression
substituted_expr = x.subs(y, 2)
print(substituted_expr)  # Output: 22
