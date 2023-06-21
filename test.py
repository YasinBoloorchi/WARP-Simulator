def parse_file(filename):
    slots = []
    current_slot = {}
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('release'):
                if current_slot:
                    slots.append(current_slot)
                    current_slot = {}
                current_slot['release'] = line
            elif line.startswith('push'):
                if 'push' not in current_slot:
                    current_slot['push'] = []
                current_slot['push'].append(line)
            elif line.startswith('while'):
                while_slot = {}
                while_slot['while'] = [line]
                current_slot['while'] = [line, while_slot]
                current_slot = while_slot
    if current_slot:
        slots.append(current_slot)
    return slots

# Example usage
filename = 'WARP-codes/Simple_loop.wrp'
result = parse_file(filename)
print(result)
