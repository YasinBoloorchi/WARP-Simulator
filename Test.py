def count_indent(line):
    count = 0
    for char in line:
        if char == ' ':
            count += 1
        else:
            break
    return count


def gen_list(the_list, line, indent):
    if indent == 0:
        the_list.append([line])
        return the_list

    gen_list(the_list[-1], line, indent-1)    
    return the_list
    

def recreate_indent(the_list, indent):
    for line in the_list:
        print('    '*indent,line[0])
        if len(line) > 1:
            recreate_indent(line[1:], indent+1)


with open('./WARP-codes/test_indent.wrp', 'r+') as test_file:
    test_file_lines = test_file.readlines()
    the_list = []    
    
    for line in test_file_lines:
        indent_count = count_indent(line)//4
        # print(f'({indent_count})',line.strip())    
        the_list = gen_list(the_list, line.strip(), indent_count)
    print(the_list)
        
        
    print('='*50)
    recreate_indent(the_list, 0)

# [['1', ['2', ['3', ['4']], ['5']], ['6']], ['7'], ['8'], ['9', ['10']]]