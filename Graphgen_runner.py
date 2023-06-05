from Graphgen import Node, State, StatesTree
from Parser import parse_instructions, inst_parser
from time import sleep
import subprocess


def run_slot(tree, slot):
    pull_count = 0
    
    for inst in slot:
        inst_type = inst[0]
        instruction = inst[1]
        print('\n\n[! Inst] ',inst, '| inst type: ', inst_type, '| instruction: ', instruction)
        
        if inst_type == 'release':
            parsed_instruction = inst_parser(instruction)[0]
            # inst_parser => [('release', 'F0', 'BA', '')]
        
            flow_name = parsed_instruction[1]+parsed_instruction[2]
            
            # workload[flow_name] = {'source': address[0], 'dest':address[1], 'has':False}
            
            tree.release_flow(flow_name)
            
        
        elif inst_type == 'drop':
            parsed_instruction = inst_parser(instruction)[0]
            # inst_parser => [('drop', 'F0', 'BA', '')] 
            
            flow_name = parsed_instruction[1]+parsed_instruction[2]
            
            tree.drop_flow(flow_name)


        elif inst_type == 'pull' or inst_type == 'push':
            pull_count += 1
            parsed_instruction = inst_parser(instruction)
            # inst_parser => [('pull', 'F0', 'BA', '#0')] 
            
            instruc, flow_number, nodes, channel_number = parsed_instruction = inst_parser(instruction)[0]
            flow_name =flow_number + nodes
            tree.add_pull_state(prob=0.8, flow_name=flow_name, inst=instruction)
            
            
        elif inst_type == 'if':
            pull_count += 1
            parsed_instruction = inst_parser(instruction)
            # inst_parser => [('has', 'F0', 'BA', ''), ('pull', 'F0', 'BA', '#1'), ('pull', 'F0', 'AC', '#1')] 
            
            condition, condition_is_true, condition_is_false = inst_parser(instruction)         

            #          F0         pull(F0,#1)         pull (F1,#1)
            #         vvvv         vvvvvvvv              vvvv
            # print(condition, condition_is_true, condition_is_false)
            
            flow_name = condition[1]
            nodes = condition[2]
            flow_name += nodes
            condition = flow_name
            
            tree.add_conditional_state(condition, condition_is_true, condition_is_false, prob=0.8)


        elif inst_type == 'sleep':
            print(instruction)
            tree.add_sleep_state(inst='sleep')

        if pull_count > 1:
            raise Exception('Unexceptable number of pull/push requests in a single slot.')
    
    
# Running the instructions that been parsed from the file
def run_loop(instruction_file_path):
    # initial variables
    instructions = parse_instructions(instruction_file_path)
    
    instructions.insert(0, [('release', 'release (F0,CA)')])

    # Generate States tree and initial state    
    tree = StatesTree()
    
    # warp code execution losiop
    for slot in instructions:

        run_slot(tree, slot)    
        
    tree.visualize_tree()

    print('Hash table:', tree.hash_table)


def main():
    run_loop('./WARP-codes/pulls.wrp')
    # subprocess.run(["pkill", "viewnior"])


if __name__ == "__main__":
    # parse_instructions('./Instructions.wrp')
    main()
