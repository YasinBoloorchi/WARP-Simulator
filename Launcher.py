from Simulator import State, Simulator
# from Old_Parser import parse_instructions, inst_parser, recreate_file
from Parser import file_parser, recreate_file
from time import sleep
from sympy import symbols, factor, expand
import subprocess

# ======== Step one ==========
def simple_while_loop():
    simu = Simulator()
    hash_table = dict()  
    
    # WARP Code:
    hash_table = simu.release('F0AB', hash_table, tick_clock_flag=False)
    
    while(True):
        hash_table = simu.pull('F0AB', tick_clock_flag=True, hash_table=hash_table)
    
        sleep(2)
        
        simu.imprint_hash_table(hash_table)
        simu.visualize_dag('./Whileloop',prob=1)
        
    
        
# ======== Step two ==========
def while_with_condition():
    simu = Simulator()
    hash_table = dict()
    clock = 0
    
    # WARP Code:
    hash_table = simu.release('F0AB', hash_table, tick_clock_flag=False)
    
    while(True):
        print(clock)
        if clock % 100 == 0:
            hash_table = simu.pull('F0AB', tick_clock_flag=True, hash_table=hash_table, tick_num=1)
            
            simu.imprint_hash_table(hash_table)
            simu.visualize_dag(f'./while_with_condition_{clock}_clock',prob=1)
        
            hash_table = simu.add_sleep(tick_clock_flag=True, hash_table=hash_table, tick_num=99)
            sleep(2)
            
        if clock == 200:
            return hash_table
        
        clock += 1


# ===== Step two =====
def while_with_controled_frequency(S=100, R=100):
    print(f'Running simulation for S={S} and R={R}')
    clock = 0
    q = list()
    hash_table = dict()
    simu = Simulator()
    
    hash_table = simu.release('F0AB', hash_table, tick_clock_flag=False)
    
    while(True):
        if clock % R == 0:
            q.append('F0AB')

        if clock % S == 0:
            print('Clock: ', clock, 'Queue: ',q)
            if q: #not empty
                p = q.pop(0)
                hash_table = simu.pull(p, tick_clock_flag=True, hash_table=hash_table, tick_num=1)
                hash_table = simu.add_sleep(tick_clock_flag=True, hash_table=hash_table, tick_num=S-1)
            
            else:
                hash_table = simu.add_sleep(tick_clock_flag=True, hash_table=hash_table, tick_num=S)
        
        
        
        
        if clock == 1000:
            simu.imprint_hash_table(hash_table, prob=0.9)
            # simu.visualize_dag(f'./controled_frequency_S{S}_R{R}',prob=0.9)
            sleep(0.5)
            return hash_table
        
        clock += 1


    
def simulate(file_name, instructions_slots):
    # Generate States simu and initial state    
    simu = Simulator()
    
    hash_table = {}
    # warp code execution losiop
    for slot in instructions_slots:
        hash_table = simu.run_slot(slot, hash_table)
        simu.imprint_hash_table(hash_table)
        print('Test of Correctness: ', simu.test_of_correctness(hash_table), end='\n'+"="*50+'\n')
    
    # sleep(0.5)
    simu.visualize_dag(file_name, prob=1)
    # simu.archive_print()
    del(simu)
    return


def run_loop(instruction_file_path):
    """
        Running the instructions that been parsed from the file
    """
    
    # initial variables
    
    file_name = instruction_file_path.split('/')[-1]
    instructions_slots = file_parser(instruction_file_path)

    print(instructions_slots)
    print('='*50)
    for slot in instructions_slots:
        # recreate_file(slot)
        print(slot)
        print('----')

    print('='*50)
    
    simulate(file_name, instructions_slots)

    return


def main():
    # ========== Costum simulations ===========
    
    # === Step one ===
    # simple_while_loop()
    
    # === Step two ===
    # while_with_condition()
    
    # === Step three ===
    while_with_controled_frequency(S=100, R=100)
    
    # Answer the same questions for
    #           R=100 S=50 and 
    #           R=50 S=100.
    
    while_with_controled_frequency(S=50, R=100)
    
    while_with_controled_frequency(S=100, R=50)
        
    # ============== Test Cases ===============
    
    # run_loop('./WARP-codes/pulls.wrp') # Passed ✓
    # run_loop('./WARP-codes/two_pulls.wrp') # Passed ✓
    # run_loop('./WARP-codes/half_condition.wrp') # Passed ✓
    # run_loop('./WARP-codes/full_condition.wrp') # Passed ✓
    # run_loop('./WARP-codes/PenTest.wrp') # Passed ✓
    # run_loop('./WARP-codes/Simple_loop.wrp') # Passed ‍‍‍✓
    # run_loop('./WARP-codes/new_half_condition.wrp') # Testing ‍‍‍~ 
    # run_loop('./WARP-codes/new_full_condition.wrp') # Testing ‍‍‍~ 
    # run_loop('./WARP-codes/four_different_state.wrp')
    # subprocess.run(["pkill", "viewnior"])


if __name__ == "__main__":
    # parse_instructions('./Instructions.wrp')
    main()