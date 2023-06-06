from Simulator import State, StatesCollection
from Parser import parse_instructions, inst_parser
from time import sleep
import subprocess


def run_slot(tree, slot):
    pull_count = 0
    
    for inst in slot:
        inst_type = inst[0]
        instruction = inst[1]
        print('\n\n[Inst] ',inst, '| inst type: ', inst_type, '| instruction: ', instruction)
        
        if inst_type == 'release':
            parsed_instruction = inst_parser(instruction)[0]
            # inst_parser => [('release', 'F0', 'BA', '')]
        
            flow_name = parsed_instruction[1]+parsed_instruction[2]
            
            # workload[flow_name] = {'source': address[0], 'dest':address[1], 'has':False}
            
            tree.release(flow_name)
            
        
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
            tree.pull(flow_name=flow_name, prob=0.8)
            
        
        elif inst_type == 'if':
            pull_count += 1
            parsed_instruction = inst_parser(instruction)
            # inst_parser => [('has', 'F0', 'BA', ''), ('pull', 'F0', 'BA', '#1'), ('pull', 'F0', 'AC', '#1')] 
            
            condition, condition_is_true, condition_is_false = inst_parser(instruction)         

            #          F0         pull(F0,#1)         pull (F1,#1)
            #         vvvv         vvvvvvvv              vvvv
            # print(condition, condition_is_true, condition_is_false)
            
            condition_flow_name = condition[1]+condition[2]
            condition_is_true_flow_name = condition_is_true[1]+condition_is_true[2]
            condition_is_false_flow_name = condition_is_false[1]+condition_is_false[2]
            
            tree.conditional_pull(condition_flow_name, condition_is_true_flow_name, condition_is_false_flow_name, prob=0.8)


        elif inst_type == 'sleep':
            # print(instruction)
            # tree.add_sleep_state(inst='sleep')
            pass
        
        
        if pull_count > 1:
            raise Exception('Unexceptable number of pull/push requests in a single slot.')
    
    
# Running the instructions that been parsed from the file
def run_loop(instruction_file_path):
    # initial variables
    instructions = parse_instructions(instruction_file_path)
    
    # instructions.insert(0, [('release', 'release (F0,CA)')])

    # Generate States tree and initial state    
    tree = StatesCollection()
    
    # warp code execution losiop
    for slot in instructions:

        run_slot(tree, slot)    
        
        # sleep(0.5)
        # tree.visualize()

        print('Hash table:')
        for state in tree.hash_table:
            print('\t',state, '|',tree.hash_table.get(state).prob, '|',tree.hash_table.get(state))
        
        
        print('Test of Correctness result: ', test_of_correctness(tree))
        print('='*50)


def test_of_correctness(tree):
    sum_of_probabilities = 0
    for state in tree.hash_table:
        sum_of_probabilities += tree.hash_table.get(state).prob
    
    if sum_of_probabilities == 1:
        return '\033[92m'+'Correct'+'\033[0m'
    else:
        return '\033[91m'+'Failed'+'\033[0m'
        

def main():
    # run_loop('./WARP-codes/pulls.wrp') # Passed ✓
    # run_loop('./WARP-codes/two_pulls.wrp') # Passed ✓
    # run_loop('./WARP-codes/one_condition.wrp') # Passed ✓ 
    run_loop('./WARP-codes/half_condition.wrp') # Passed ✓
    
    
    # subprocess.run(["pkill", "viewnior"])


if __name__ == "__main__":
    # parse_instructions('./Instructions.wrp')
    main()
