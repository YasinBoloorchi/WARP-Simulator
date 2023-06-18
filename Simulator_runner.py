from Simulator import State, StatesCollection
from Parser import parse_instructions, inst_parser
from time import sleep
from sympy import symbols, factor, expand
import subprocess


        
    
# Running the instructions that been parsed from the file
def run_loop(instruction_file_path):
    # initial variables
    file_name = instruction_file_path.split('/')[-1]
    instructions = parse_instructions(instruction_file_path)
    
    # instructions.insert(0, [('release', 'release (F0,CA)')])

    # Generate States simu and initial state    
    simu = StatesCollection()
    
    # warp code execution losiop
    for slot in instructions:

        simu.run_slot(slot)    
        
        # sleep(0.5)
        # simu.visualize()

        print('Hash table:')
        success_prob = symbols('S')
        for state in simu.hash_table:
            print('\t',state, '|',
                  simu.hash_table.get(state).workload,'|',
                  factor(simu.hash_table.get(state).prob), '|',
                  round(factor(simu.hash_table.get(state).prob).subs(success_prob, 0.8), 3), '|',
                  simu.hash_table.get(state))
        
        
        print('Test of Correctness result: ', test_of_correctness(simu))
        print('='*50)
        
    
    # sleep(0.5)
    simu.visualize_dag(file_name, prob=0.8)
        
    print('Archive root is:', simu.root.id, simu.root)
    print('Length of Archive is:', len(simu.archive))
    for state in simu.archive:
        print('ID: ',state.id, state.clock, state)
        
        if state.left:
            print('\tLeft ID: ',state.left.id, state.clock, state.left)
        
        if state.right:
            print('\tRight ID: ', state.right.id, state.clock, state.right)
        print('-'*50)


def test_of_correctness(simu):
    sum_of_probabilities = 0
    for state in simu.hash_table:
        sum_of_probabilities += simu.hash_table.get(state).prob
    
    if factor(sum_of_probabilities) == 1:
        return '\033[92m'+'Correct'+'\033[0m'
    else:
        return '\033[91m'+'Failed'+'\033[0m'
        

def main():
    # Testing Codes
    # run_loop('./WARP-codes/pulls.wrp') # Passed ✓
    # run_loop('./WARP-codes/two_pulls.wrp') # Passed ✓
    run_loop('./WARP-codes/half_condition.wrp') # Passed ✓
    # run_loop('./WARP-codes/full_condition.wrp') # Passed ✓  
    # run_loop('./WARP-codes/Simple_loop.wrp') # Testing ‍‍‍~ 
    
    # subprocess.run(["pkill", "viewnior"])


if __name__ == "__main__":
    # parse_instructions('./Instructions.wrp')
    main()