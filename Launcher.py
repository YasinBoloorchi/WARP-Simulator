import subprocess
from time import sleep

from sympy import expand, factor, symbols

# from Old_Parser import parse_instructions, inst_parser, recreate_file
from Parser import file_parser, recreate_file
from Simulator import Simulator, State


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


# ===== Step three =====
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


# ===== Step four =====
def while_with_controled_frequency_new(S=100, R=100, t=0, t_plus=200):
    print(f'Running simulation for S={S} and R={R}')
    clock = t
    q = list()
    simu = Simulator()
    hash_table = dict({simu.root.id:simu.root})
    sleep_count = 0
    flow_counter = 0
    
    if t > 0:
        hash_table = simu.add_sleep(tick_clock_flag=True, hash_table=hash_table, tick_num=t)
    
    while(True):
        if clock % R == 0:
            if sleep_count > 0:
                hash_table = simu.add_sleep(tick_clock_flag=True, hash_table=hash_table, tick_num=sleep_count)
                sleep_count = 0    
            # q.append(f'F{flow_counter}AB')
            hash_table = simu.release(f'F{flow_counter}AB', hash_table, tick_clock_flag=False, tick_num=0)
            # for state in hash_table:
            #     hash_table.get(state).queue.append(f'F{flow_counter}AB')
            
            flow_counter += 1

        if clock % S == 0:
            if sleep_count > 0:
                hash_table = simu.add_sleep(tick_clock_flag=True, hash_table=hash_table, tick_num=sleep_count)
                sleep_count = 0    
            hash_table = simu.pull('', tick_clock_flag=True, hash_table=hash_table, tick_num=1)
        else:
            sleep_count += 1
        
        
        if clock == t_plus:
            if sleep_count > 0:
                hash_table = simu.add_sleep(tick_clock_flag=True, hash_table=hash_table, tick_num=sleep_count)
                
            simu.imprint_hash_table(hash_table, prob=0.9)
            simu.visualize_dag(f'./controled_frequency_S{S}_R{R}_t{t}_tPlus{t_plus}',prob=0.9)
            simu.test_of_correctness(hash_table=hash_table, std_out=True)
            # sleep(0.5)
            return hash_table
        
        clock += 1



# === Step five ====
def while_with_conditional_split(S=100, R=100, t=0, t_plus=200):
    print(f'Running simulation for S={S} and R={R}')
    clock = 0
    q = list()
    simu = Simulator()
    hash_table = dict({simu.root.id:simu.root})
    sleep_count = 0
    flow_counter = 0
    
    # if t > 0:
    #     hash_table = simu.add_sleep(tick_clock_flag=True, hash_table=hash_table, tick_num=t)
    
    while(True):
        if clock % R == 0:
            condition_name = f't%{clock}R'
            flow_name = f'F{flow_counter}AB'
            
            # add skipped sleeps
            if sleep_count > 0:
                hash_table = simu.add_sleep(tick_clock_flag=True, hash_table=hash_table, tick_num=sleep_count-1)
                sleep_count = 0
                
            # Split the states based on condition
            hash_table = simu.c_split(condition_name, tick_clock_flag=False, hash_table=hash_table)
            
            for state_id in list(hash_table.keys()):
                state = hash_table.get(state_id)
                
                if not state.conditions[condition_name]: # It's reverse be cause we DO when mod is 0
                    hash_table = simu.single_release(flow_name=flow_name, hash_table=hash_table, state=state, tick_clock_flag=True, tick_num=0)
                else:
                    hash_table = simu.single_sleep(tick_clock_flag=True, hash_table=hash_table, state=state, tick_num=0)
            
            # for state in hash_table:
            #     hash_table.get(state).queue.append(f'F{flow_counter}AB')
            
            flow_counter += 1

        if clock % S == 0:
            
            # Add skipped sleeps
            if sleep_count > 0:
                hash_table = simu.add_sleep(tick_clock_flag=True, hash_table=hash_table, tick_num=sleep_count-1)
                sleep_count = 0   
            
            # Split the states based on condition    
            hash_table = simu.c_split(f't%{clock}S', tick_clock_flag=False, hash_table=hash_table)
            
            hash_table = simu.pull('', tick_clock_flag=True, hash_table=hash_table, tick_num=1)
            # for state_id in list(hash_table.keys()):
            #     state = hash_table.get(state_id)
                
            #     if len(state.queue)>0:
            #         hash_table = simu.apply_pull(state.queue[0], tick_clock_flag=True, state=state, hash_table=hash_table, tick_num=1)
            #     else:
            #         hash_table = simu.single_sleep(tick_clock_flag=True, hash_table=hash_table, state=state, tick_num=1)
                
                
        # else:
        sleep_count += 1
        
        
        if clock == t_plus:
            if sleep_count > 0:
                hash_table = simu.add_sleep(tick_clock_flag=True, hash_table=hash_table, tick_num=sleep_count)
                
            simu.imprint_hash_table(hash_table, prob=0.9)
            simu.visualize_dag(f'./controled_frequency_S{S}_R{R}_t{t}_tPlus{t_plus}',prob=0.9)
            simu.test_of_correctness(hash_table=hash_table, std_out=True)
            # sleep(0.5)
            return hash_table
        
        clock += 1


def kowsars_work():
    
    simu = Simulator()
    hash_table = dict({simu.root.id:simu.root})
    
    hash_table = simu.release('F0BA', hash_table=hash_table, tick_clock_flag=True, tick_num=1)
    
    
    simu.visualize_dag()
    
    

    
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
    simu.visualize_dag(file_name, prob=0.8)
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
    # while_with_controled_frequency(S=100, R=100)
    
    
    # === Step four ===
    while_with_controled_frequency_new(S=50, R=100, t=0, t_plus=150)
    
    # === Step five ===
    # while_with_conditional_split(S=100, R=100, t=0, t_plus=100)
    
    
    # === Kowsar's ==
    # kowsars_work()

    # Answer the same questions for
    #           R=100 S=50 and 
    #           R=50 S=100.
    
    # while_with_controled_frequency(S=50, R=100)
    
    # while_with_controled_frequency(S=100, R=50)
        
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
