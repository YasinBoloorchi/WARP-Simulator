import subprocess
from time import sleep

from sympy import expand, factor, symbols

# from Old_Parser import parse_instructions, inst_parser, recreate_file
from Parser import file_parser, recreate_file
from Simulator import Simulator, State
from datetime import datetime

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
def while_with_condition(end_clock):
    simu = Simulator()
    hash_table = dict()
    clock = 0
    
    # WARP Code:
    hash_table = simu.release('F0AB', hash_table, tick_clock_flag=False)
    
    while(True):
        print(clock)
        if clock % 100 == 0:
            hash_table = simu.pull('F0AB', tick_clock_flag=True, hash_table=hash_table, tick_num=1, threshold=0)
            
            hash_table = simu.add_sleep(tick_clock_flag=True, hash_table=hash_table, tick_num=99)
            # sleep(2)
            
        if clock == end_clock:
            simu.imprint_hash_table(f'while_with_condition_{clock}_clock',hash_table)
            simu.visualize_dag(f'./while_with_condition_{clock}_clock', const_prob=0.6)
        
            return hash_table
        
        clock += 1

# ===== Step Two (Under construction) =====
def while_with_condition(end_clock, RS=100):
    simu = Simulator()
    hash_table = dict()
    clock = 0
    sleep_time = 0
    # WARP Code:
    hash_table = simu.release('F0AB', hash_table, tick_clock_flag=False)
    
    while(True):
        if clock % RS == 0:
            if sleep_time > 0:
                hash_table = simu.add_sleep(tick_clock_flag=True, hash_table=hash_table, tick_num=sleep_time-1)
                sleep_time = 0
                
            hash_table = simu.pull('F0AB', tick_clock_flag=True, hash_table=hash_table, tick_num=1, threshold=0)
            
            
        if clock == end_clock:
            simu.imprint_hash_table(f'while_with_condition_{clock}_clock',hash_table)
            simu.visualize_dag(f'./while_with_condition_{clock}_clock', const_prob=0.6)
        
            return hash_table
        
        clock += 1
        sleep_time +=1


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
def while_with_conditional_split(S=100, R=100, t_plus=200, sc_threshold=0.1):
    # print(f'Running simulation for S={S} and R={R}')
    today_date = datetime.now().strftime('%B_%d')
    simulation_name = f'{today_date}_S_{S}_R_{R}_clocks_{t_plus}'
    
    print(simulation_name)
    clock = 0
    q = list()
    simu = Simulator()
    hash_table = dict({simu.root.id:simu.root})
    sleep_count = 0
    flow_counter = 0
    const_prob = 0.8
    threshold = 0.2
    release_curve = list()
    push_curve = list()
    service_curve = list()
    # Initial release 
    # for i in range(5):
    #     hash_table = simu.release(f'F{i}AA', hash_table)
    
    
    while(True):
        print("Clock: ", clock)
        print('Length of hash_table: ', len(hash_table))    
        
        ##### if clock % R == 0: Release Section
        R_condition_name = f'(t+{clock})%{R}'
        flow_name = f'F{flow_counter}AB'
        
        # Split the states based on condition
        hash_table = simu.c_split(R_condition_name, tick_clock_flag=False, hash_table=hash_table)

        for state in list(hash_table.values()):
            if R_condition_name+"==0" in state.conditions:
                hash_table = simu.single_release(flow_name=flow_name, hash_table=hash_table, state=state, tick_clock_flag=False, tick_num=0)
                
            else:
                hash_table = simu.single_sleep(tick_clock_flag=False, hash_table=hash_table, state=state, tick_num=0)
                
                    # hash_table = simu.add_sleep(tick_clock_flag=True, hash_table=hash_table, tick_num=1)
        flow_counter += 1
        
        # Gathering arrival curve and service curve data
        release_curve.append(simu.most_release_count(hash_table))
        push_curve.append(simu.least_push_count(hash_table, threashold=sc_threshold))

        
        # release_curve.append(simu.most_release_count(hash_table))
        
        ### End loop condition
        if clock == t_plus:
            end_loop(simulation_name, simu, hash_table, release_curve, push_curve, sc_threshold)
            return hash_table
        
        ##### if clock % S == 0: Push section
        S_condition_name = f'(t+{clock})%{S}'
        
        # Split the states based on condition
        hash_table = simu.c_split(S_condition_name, tick_clock_flag=False, hash_table=hash_table)

        # Apply a pull
        for state in list(hash_table.values()):                
            if S_condition_name+"==0" in state.conditions:
                # Split the states based on the nested condition for the queue
                # hash_table = simu.c_split('queue', tick_clock_flag=False, hash_table=hash_table)

                hash_table = simu.single_pull(state, '', tick_clock_flag=True, hash_table=hash_table, tick_num=1, const_prob=const_prob)

            else:
                hash_table = simu.single_sleep(tick_clock_flag=True, hash_table=hash_table, state=state, tick_num=1)
            
        
        # service_curve.append(simu.least_push_count(hash_table, const_prob, 0.23))
        
        
        
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
        simu.imprint_hash_table(file_name, hash_table)
        print('Test of Correctness: ', simu.test_of_correctness(hash_table), end='\n'+"="*50+'\n')
    
    # sleep(0.5)
    simu.visualize_dag(file_name, const_prob=0.8)
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


def end_loop(simulation_name, simu, hash_table, release_curve, push_curve, sc_threshold):
    
    # ?????????????????????????????????????????????????????????????
    # simu.test_of_correctness(hash_table=hash_table, std_out=True)
    # simu.test_of_correctenss2(hash_table, std_out=False)
    # ?????????????????????????????????????????????????????????????
    
    # LOG |||| ||||| ||||| |||||||||||| |||||||| || ||||||||||||||||||||||
    # simu.imprint_hash_table(simulation_name, hash_table, const_prob=0.8)
    
    
    
    print("release_curve: ", release_curve)
    # x                    , y                    , z
    # largest_release_clock, largest_release_count, largest_release_model
    #   ^    ____
    #   |___/
    #   |
    #   |---------->
    release_curve_2d_data = [(x, y) for x, y, z in release_curve]
    print(release_curve_2d_data)
    simu.plot_release_curve_2D(release_curve_2d_data, simulation_name)
    
    # Push Curve
    #   ^
    #   |     ____
    #   |____/
    #   |---------->
    # print("Push curve:    ", push_curve)
    push_curve_2d_data = [(x, y) for x, y, z in push_curve]
    simu.plot_push_curve_2D(push_curve_2d_data, simulation_name)
    
    
    #     ___ 
    #    /__/|
    #    |__|/
    # release_curve_3d_data = [(z, str(x), y) for x, y, z in release_curve]
    # print("release_curve_3d_data: ", release_curve_3d_data)
    # simu.plot_release_curve_3D(release_curve_3d_data)
    
    # simu.find_release_curve(hash_table)
    # simu.paths_to_curves(hash_table)
    # simu.plot_all_curves(hash_table, simulation_name, threshold=0)
    # simu.plot_all_curves(hash_table, simulation_name, threshold=0.3)
    
    
    # Arrival Curve
    #   ^      __
    #   |   __/
    #   |__/
    #   |---------->
    release_curve_1d_data =  [y for x, y, z in release_curve]
    ac = simu.get_arrival_curve(release_curve_1d_data)
    print("Arrival curve: ", ac)
    simu.plot_arrival_curve(ac, simulation_name)
    
    
    # Service Curve
    #   ^      __
    #   |   __/
    #   |__/
    #   |---------->
    push_curve_1d_data = [y for x, y, z in push_curve]
    print("push_curve_1d_data: ", push_curve_1d_data)
    sc = simu.get_service_curve(push_curve_1d_data, verbose=False)
    print("Service curve: ", sc)
    simu.plot_service_curve(sc, simulation_name, curve_name='Service Curve')
    
    
    # Service Curve with DFS
    #   ^      __       |#               ( )
    #   |   __/         |#              /   \\
    #   |__/            |#           ( )     ( )
    #   |---------->    |#          /   \   //  \
    #   |               |#        ( )  ( ) ( )  ( )
    #
    #
    all_founded_paths = simu.find_all_paths(hash_table, sc_threshold)
    all_founded_paths_push_data = simu.all_paths_to_push_data(all_founded_paths)
    # least_founded_path_push_data = simu.least_path_push_data(all_founded_paths_push_data)
    # print("least_founded_path_push_data: ", least_founded_path_push_data)
    
    # sc = simu.get_service_curve(least_founded_path_push_data, verbose=False)
    # print("DFS Service curve: ", sc)
    # simu.plot_service_curve(sc, simulation_name+"_DFS", curve_name='DFS Service Curve')
    
    all_service_curves = list()
    path_counter = 0
    for path in all_founded_paths_push_data:
        # print("path: ", path)
        path_counter += 1
        sc = simu.get_service_curve(path, verbose=False)
        all_service_curves.append(sc)
        print(f'Service Curve #{path_counter}: ', sc)
        # simu.plot_service_curve(sc, simulation_name+"_DFS"+f"_Path#{path_counter}", curve_name=f'DFS Service Curve #{path_counter}')
        
    print("Minimum service curve: " ,min(all_service_curves))
    simu.plot_service_curve(min(all_service_curves), simulation_name+"_DFS", curve_name='DFS Service Curve')
    
    
    # DAG Viz
    #               ( )
    #              /   \
    #           ( )     ( )
    #          /   \   /   \
    #        ( )  ( ) ( )  ( )
    simu.visualize_dag(simulation_name)
    
    
    
    # DAG Viz
    #               ( )
    #              /   \\
    #           ( )     ( )
    #          /   \   //  \
    #        ( )  ( ) ( )  ( )
    # --- Verify every single curve by visualizing them all (TIME CONSUMING)
    # All possible paths
    # all_founded_paths = simu.find_all_paths(hash_table, threshold=0.3)
    # path_counter = 0
    # for path in all_founded_paths:
    #     simu.visualize_dag(simulation_name+f'Path#{path_counter}', path_trace=path)
    #     path_counter += 1
            

def main():
    # ========== Costum simulations ===========
    
    # === Step one ===
    # simple_while_loop()
    
    # === Step two ===
    # while_with_condition(end_clock=200, RS=50)
    
    # === Step three ===
    # while_with_controled_frequency(S=100, R=100)
    
    
    # === Step four ===
    # while_with_controled_frequency_new(S=50, R=100, t=0, t_plus=150)
    
    # === Step five ===
    
    
    while_with_conditional_split(S=1, R=5, t_plus=10, sc_threshold=0.012)
    
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
