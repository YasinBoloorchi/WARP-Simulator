from Simulator import State, Simulator
from Parser import parse_instructions, inst_parser
from time import sleep
from sympy import symbols, factor, expand
import subprocess



def simulate(file_name, instructions):
    # Generate States simu and initial state    
    simu = Simulator()
    
    # warp code execution losiop
    for slot in instructions:
        simu.run_slot(slot)
        simu.imprint_hash_table()
        print('Test of Correctness result: ', simu.test_of_correctness(), end='\n'+"="*50+'\n')
    
    # sleep(0.5)
    simu.visualize_dag(file_name, prob=1)
    simu.archive_print()



def run_loop(instruction_file_path):
    """
        Running the instructions that been parsed from the file
    """
    
    # initial variables
    
    file_name = instruction_file_path.split('/')[-1]
    instructions = parse_instructions(instruction_file_path)

    simulate(file_name, instructions)



def main():
    # Testing Cases
    # run_loop('./WARP-codes/pulls.wrp') # Passed ✓
    # run_loop('./WARP-codes/two_pulls.wrp') # Passed ✓
    # run_loop('./WARP-codes/half_condition.wrp') # Passed ✓
    run_loop('./WARP-codes/full_condition.wrp') # Passed ✓
    # run_loop('./WARP-codes/PenTest.wrp') # Passed ✓
    # run_loop('./WARP-codes/Simple_loop.wrp') # Testing ‍‍‍~ 
    
    # subprocess.run(["pkill", "viewnior"])


if __name__ == "__main__":
    # parse_instructions('./Instructions.wrp')
    main()