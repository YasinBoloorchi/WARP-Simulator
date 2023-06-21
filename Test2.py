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
        the_list.append(line)
        return the_list
    
    if indent - 1 == 0:
        the_list.append([])

    gen_list(the_list[-1], line, indent-1)    
    return the_list
    

def recreate_indent(the_list, indent):
    for i in range(len(the_list)):
        print('    '*indent,the_list)
        print('    '*indent,the_list[i][0])
        
        if the_list[i][1]:
            recreate_indent(the_list[i][1].copy(), indent+1)

    return


with open('./WARP-codes/test_indent.wrp', 'r+') as test_file:
    test_file_lines = test_file.readlines()
    the_list = []    
    
    for line in test_file_lines:
        indent_count = count_indent(line)//4
        print(f'({indent_count})',line.strip())    
        the_list = gen_list(the_list, line.strip(), indent_count)
        print(the_list)
        
        
    # print('='*50)
    # recreate_indent(the_list, 0)
    
# ['1', ['2', ['3', ['4']], ['5']], ['6'], '7', '8', '9', ['10']]