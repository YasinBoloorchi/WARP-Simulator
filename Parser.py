import re

# Parsing the Warp instruction from a file
def parse_instructions(instruction_file_path):
    with open(instruction_file_path, 'r') as instructions_file:
        instructions = [inst.strip() for inst in instructions_file.readlines()]
        
        # instructions = [[inst.split(' ', maxsplit=1)[0], inst.strip()] for inst in instructions_file.readlines() if inst.strip()]
        # print(instructions)
        
        slot_num = 0
        slots = [[]]
        
        for inst in instructions:
            if '--' in inst:
                slot_num += 1
                slots.append([])
            else:
                instruction = (inst.split(' ', maxsplit=1)[0], inst.strip())
                slots[slot_num].append(instruction)
                
        instructions = slots.copy()
        instructions_file.close()
        
    return instructions

# Parser function for different types of instructions
def inst_parser(instruction):
    parsed_inst = re.findall('(\w*)\s*\(\s*(\w\d+)\s*,*\s*(\w+)*\s*,*(\#\d+)*\s*\)', instruction)
    
    # print('\n\n','Parsed ====>',parsed_inst,'\n\n')
    return parsed_inst


def if_inst_parser(instruction):
    parsd_if_inst = re.findall('^\w*\s*\W\w*\((\w\d),\w{2}\)\s*\w*\s*(\w*\s*\(\s*\w+\d+\s*,\s*\W\d+,\w{2}\))\s*\w*\s*(\w*\s*\(\s*\w+\d+\s*,\s*\W\d+,\w{2}\))*$', instruction)[0]
    
    return parsd_if_inst
