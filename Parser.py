import re



# Parsing the Warp instruction from a file
def parse_instructions(instruction_file_path):
    with open(instruction_file_path, 'r') as instructions_file:
        instructions = [inst.strip() for inst in instructions_file.readlines()]
        
        slot_num = 0
        slots = [[]]
        
        for inst in instructions:
            if '---' in inst:
                slot_num += 1
                slots.append([])
            else:
                instruction = (inst.split(' ', maxsplit=1)[0], inst.strip())
                slots[slot_num].append(instruction)
                
        instructions = slots.copy()
        instructions_file.close()
        
    return instructions


def count_indent(inst):
    """Counts number of spaces befor each instruction"""
    count = 0
    for char in inst:
        if char == ' ':
            count += 1
        else:
            break
    print(count)
    return count

def push_instruction(inst, indent):
    if indent < 0:
        return instruction
    
    inst_type = inst.split(' ', maxsplit=1)[0]
    
    instruction =  {inst_type: [inst.strip()]}
    


# each slot = []
# each slot = [ {} ]
# each slot = [ {inst_type: [] } ]
# each slot = [ {inst_type: [instruction] } ]

# each slot = [ {'release': "release (F0, AB)" } ]

# each slot = [ {'push': ["push (F0, AB)"] } ]

# each slot = [   {  'while':  ['while (50)', {'push': ["push (F0, AB)"]} ]    } ]

# slots = [ {'release': "release (F0, AB)" } , 
#           {'push': ["push (F0, AB)"] } , 
#           {  'while':  ['while (50)', {'push': ["push (F0, AB)"]} ]    
#           } 
#         ] 

# each slot = [   {  'while(50)':  [ {'if1': ['push1']} ]    } ]
# each slot = [   { 'while(50)': [{'if1': ['push1']}, {'if2': ['push2']}] }   ]
def new_parse_instructions(instruction_file_path):
    with open(instruction_file_path, 'r') as instructions_file:
        instructions = [inst.replace('\n', '') for inst in instructions_file.readlines()]

        slot_num = 0
        above_line = 0
        slots = [[]]
        
        for inst in instructions:
            if len(inst.strip()) == 0:
                # It's an empty line
                continue
            
            elif '---' in inst:
                # It's a new slot
                slot_num += 1
                above_line = 0
                slots.append([])
                
            else:
                # It's a line of instruction
                # push_instruction(inst, count_indent(inst))
                
                instruction = [inst.split(' ', maxsplit=1)[0], inst.strip()]
                
                
                
                
                slots[slot_num].append(instruction)
                above_line += 1
                
        instructions = slots.copy()
        instructions_file.close()
        
        for i in instructions:
            print(i)
    exit()
    # return instructions

# Parser function for different types of instructions
def inst_parser(instruction):
    parsed_inst = re.findall('(\w*)\s*\(\s*(\w\d+)\s*,*\s*(\w+)*\s*,*(\#\d+)*\s*\)', instruction)
    
    
    if len(parsed_inst) == 2:
        parsed_inst.append(('', '', '', ''))
    
    # print('\n\n','Parsed ====>',parsed_inst,'\n\n', 'Len: ', len(parsed_inst))
    
    return parsed_inst
