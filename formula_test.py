from sympy import symbols, factor, expand

success_prob = symbols('S')
fail_prob = 1 - success_prob

expresion = success_prob * success_prob + success_prob

print(expresion.subs(success_prob, 0.8))