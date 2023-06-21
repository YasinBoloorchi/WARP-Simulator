import re

"""
release (F0, AB)
----
while (True):
    push (F0, AB)
----

v v v v v v v v v v v v v v v v v v v

[[['release (F0, AB)']], [['while (True):', ['push (F0, AB)']]]]

# [['1', ['2', ['3', ['4']], ['5']], ['6']], ['7'], ['8'], ['9', ['10']]]
"""

def count_indent(line):
    count = 0
    for char in line:
        if char == ' ':
            count += 1
        else:
            break
    return count


def gen_list(inst_list, line, indent):
    if indent == 0:
        inst_list.append([line])
        return inst_list

    gen_list(inst_list[-1], line, indent-1)    
    return inst_list
    

def recreate_file(slot, indent=0):
        for line in slot:
            print('    '*indent,line[0])
            if len(line) > 1:
                recreate_file(line[1:], indent+1)


def file_parser(instruction_file_path):
    with open('./WARP-codes/Simple_loop.wrp', 'r+') as test_file:
        test_file_lines = test_file.readlines()
        inst_list = []  
        
        slots = []
        # slot_num = 0
        
        for line in test_file_lines:
            if len(line.strip()) == 0:
                continue
            
            elif '---' in line:
                # slot_num += 1
                slots.append(inst_list.copy())
                inst_list = [] 
                # slots.append([])
                
            
            else:
                indent_count = count_indent(line)//4
                inst_list = gen_list(inst_list, line.strip(), indent_count)
        
        slots.append(inst_list.copy())
        # print(inst_list)    
        # print('='*50)
        # recreate_file(inst_list, 0)
        
    return slots


# Parser function for different types of instructions
def inst_parser(instruction):
    parsed_inst = re.findall('(\w*)\s*\(\s*(\w\d+)\s*,*\s*(\w+)*\s*,*(\#\d+)*\s*\)', instruction)
    
    
    if len(parsed_inst) == 2:
        parsed_inst.append(('', '', '', ''))
    
    # print('\n\n','Parsed ====>',parsed_inst,'\n\n', 'Len: ', len(parsed_inst))
    
    return parsed_inst
