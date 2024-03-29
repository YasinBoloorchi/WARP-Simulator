import copy
from collections import deque
from time import sleep

from graphviz import Digraph, Graph
from sympy import Integer, factor, symbols

from Parser import inst_parser
import hashlib
import z3

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from math import ceil

class State:
    def __init__(self, workload={}):
        self.workload = workload
        self.prob = Integer(1)
        self.prob_cons = 1
        self.path_cons = str()
        self.right = None
        self.left = None
        self.clock= symbols('t')
        self.queue = list()
        self.push_count = 0
        self.release_count = 0
        self.instruction = str()
        self.conditions=set({'t>=0'})
        self.model = dict()
        self.split_count = 0
        
        
    def tick_clock(self, tick_num):
        self.clock += tick_num

    
    def update_path_cons(self):
        # add conditions to the path constraint
        if self.conditions:
            sorted_list_of_conditions = list(self.conditions)
            sorted_list_of_conditions.sort()
            self.path_cons = ' && '.join(sorted_list_of_conditions)
        

    def get_workload_string(self):
        dictionary_keys = list(self.workload.keys())
        dictionary_keys.sort()
        sorted_dictionary = {key: self.workload[key] for key in dictionary_keys}
        key_value_strings = [f"{key}:{value}" for key, value in sorted_dictionary.items()]
        unique_string = ', '.join(key_value_strings)
        
        if unique_string == '':
            unique_string = "True"
            
        return unique_string

    def update_id(self):
        self.update_path_cons()
        # self.queue.sort()
        queue = ''.join(f'|{e[0]}' for e in self.queue)
        data = queue + " | " + self.path_cons
        sha256_hash = hashlib.sha256()
        sha256_hash.update(data.encode('utf-8'))
        result = sha256_hash.hexdigest()
        self.id = result
        
        return result

class Simulator:
    def __init__(self):
        self.archive = {}
        self.root = State()
        self.root.path_cons = 'True'
        self.root.update_id()

    def gen_hash_table(self):
        return dict({self.root.id: self.root})

    def run_slot(self, slot, hash_table={}):
        
        pull_count = 0
        tick_clock_flag = True

        # keep_clock_flag = False
        for inst in slot:
            inst_type = inst[0].split(' ', maxsplit=1)[0]
            instruction = inst[0]
            print('\n\n[Inst] ',inst, '| inst type: ', inst_type, '| instruction: ', instruction)
            
            # continuerun_slot(self, slot, hash_table={})
            
            if inst_type == 'release':
                parsed_instruction = inst_parser(instruction)[0]
                # inst_parser => [('release', 'F0', 'BA', '')]
            
                flow_name = parsed_instruction[1]+parsed_instruction[2]
                
                # workload[flow_name] = {'source': address[0], 'dest':address[1], 'has':False}
                
                hash_table = self.release(flow_name, hash_table, tick_clock_flag)
                
            
            elif inst_type == 'drop':
                parsed_instruction = inst_parser(instruction)[0]
                # inst_parser => [('drop', 'F0', 'BA', '')] 
                
                flow_name = parsed_instruction[1]+parsed_instruction[2]
                
                hash_table = self.drop_flow(flow_name, tick_clock_flag, hash_table)


            elif inst_type == 'pull' or inst_type == 'push':
                pull_count += 1
                parsed_instruction = inst_parser(instruction)
                # inst_parser => [('pull', 'F0', 'BA', '#0')] 
                
                instruc, flow_number, nodes, channel_number = parsed_instruction = inst_parser(instruction)[0]
                flow_name =flow_number + nodes
                hash_table = self.pull(flow_name, tick_clock_flag, hash_table)#, prob=0.8)
                
            
            elif inst_type == 'if':
                # pull_count += 1
                parsed_instruction = inst_parser(instruction)
                # [Inst]  ['if !has(F0,AB):', ['pull (F0,AB,#1)'], 'else:', ['pull (F0,BC,#1)']]
                print('inst: ', inst)
                print('instruction: ', instruction)
                print('Parsed Instruction in if: ', parsed_instruction)
                condition_type, condition_flow, condition_nodes, _ = inst_parser(instruction)[0]
                
                condition = condition_flow + condition_nodes
                
                print("condition_type, condition: :", condition, condition_type)
                
                
                if 'else:' in inst:
                    condition_is_true_inst = inst[1: inst.index('else:')]
                    condition_is_false_inst = inst[inst.index('else:')+1:]
                else:
                    condition_is_true_inst = inst[1:]
                    condition_is_false_inst = []
                    
                print("condition_is_true_inst, condition_is_false_inst: ", condition_is_true_inst, condition_is_false_inst)
                
                
                hash_table = self.condition(condition_type, condition, condition_is_true_inst, condition_is_false_inst, tick_clock_flag, hash_table)#, prob=0.8)


            elif inst_type == 'sleep':
                # print(instruction)
                # self.add_sleep_state(inst='sleep')
                hash_table = self.add_sleep(tick_clock_flag, hash_table)
              
                
            elif inst_type == 'while':
                # [Inst]  ['while (10):', ['push (F0, AB)']] | inst type:  while | instruction:  while (10):
                # [['while (10):', ['push (F0, AB)'], ['pull (F1, CA)']]]
                
                def check_loop_condition(condition, counter):
                    if condition == 'True':
                        condition = 100

                    
                    if int(condition) - counter > 0:
                        return True
                    else:
                        return False
            
                
                parsed_instruction = inst_parser(instruction)[0]
                
                # print('Inst_parser result: ', parsed_instruction)
                # exit()
                print('condition:', parsed_instruction[1])
                condition = parsed_instruction[1]
                counter = 0
                
                while check_loop_condition(condition, counter):
                    hash_table = self.run_slot(inst[1:], hash_table)
                    counter += 1
                
           
            if pull_count > 1:
                raise Exception('Unexceptable number of pull/push requests in a single slot.')
            
            # if not keep_clock_flag:
            tick_clock_flag = False
                # keep_clock_flag = False

            # self.hash_table = hash_table.copy()
        
        return hash_table


    def condition(self, condition_type, condition, condition_is_true_inst, condition_is_false_inst, tick_clock_flag, hash_table, prob=symbols('S')):
        
        def check_if_condition(state, condition_type, condition):
            
            if condition_type == '!has':
                if not state.workload.get(condition):
                    return True
                else:
                    return False
                
            elif condition_type == 'has':
                if state.workload.get(condition):
                    return True
                else:
                    return False


    def release(self, flow_name, hash_table, tick_clock_flag=False, tick_num=1):
        """Add the given flow_name with zero number of failure as a list
        to the queue of all the states
        """
        
        if not hash_table:
            hash_table[self.root.id] = self.root

        
        for key in list(hash_table.keys()):
            
            state = hash_table.pop(key)
            state.instruction = f'Release({flow_name})'
            new_state = copy.deepcopy(state)
            new_state.workload[flow_name] = False
            new_state.queue.append([flow_name, 0]) # add flow name & the number of failed transmition for that flow which initially is zero
            new_state.release_count += 1
            new_state.update_id()
            hash_table[new_state.id] = new_state
            
            if tick_clock_flag:
                new_state.tick_clock(tick_num)
            
            state.right = hash_table[new_state.id]
            
        return hash_table
    

    def single_release(self, flow_name, hash_table, state, tick_clock_flag=False, tick_num=1):
        """Add the given flow_name with zero number of failure as a list
        to the queue of the given states
        """
              
        state = hash_table.pop(state.id)
        
        if state.model == 'unsat':
            return hash_table
        
        state.instruction = f'Release({flow_name})'
        new_state = copy.deepcopy(state)
        new_state.workload[flow_name] = False
        new_state.queue.append([flow_name, 0]) # add flow name & the number of failed transmition for that flow which initially is zero
        new_state.release_count += 1
        new_state.update_id()
        hash_table[new_state.id] = new_state
        
        if tick_clock_flag:
            new_state.tick_clock(tick_num)
        
        state.right = hash_table[new_state.id]
        
        return hash_table

    
    def apply_pull(self, flow_name, tick_clock_flag, state, hash_table, prob=symbols('S'), tick_num=1, threshold=0, const_prob=0.8):
        """Fork the given state into two possible non-deterministic state (success or failure)
        based on the probability given and adding them to the given hashtable

        Args:
            flow_name (_type_): _description_
            tick_clock_flag (_type_): _description_
            state (_type_): _description_
            hash_table (bool): _description_
            prob (_type_, optional): _description_. Defaults to symbols('S').
            tick_num (int, optional): _description_. Defaults to 1.
            threshold (int, optional): _description_. Defaults to 0.
            const_prob (float, optional): _description_. Defaults to 0.8.

        Returns:
            _type_: _description_
        """
        
        if flow_name == '':
            state.tick_clock(tick_num)
            hash_table[state.id] = state
            return hash_table
        
        state.instruction = f'Pull ({flow_name[0]})'
        
        # -------- Copy fail_state --------
        fail_state = copy.deepcopy(state)
        # ---------------------------------
        
        # ------ Copy success_state --------
        success_state = copy.deepcopy(state)
        # ----------------------------------
        
        
        
        # ------------------------------------
        # Create a new state for success -----
        # if flow_name in state.queue: # changed from: "if state.workload[flow_name] != True:" to "if flow_name not in state.queue"
        if any(flow_name[0] == flow[0] for flow in state.queue):
            # success_state.workload[flow_name[0]] = True
            success_state.prob = success_state.prob * prob  # Multiply S probability
            success_state.queue.pop(0)
        else:
            success_state.prob *= 1
        
        # Generate unique id
        success_state.update_id()
        
        # Update new hashtable with success state (Merge section)
        if success_state.id in hash_table:
            hash_table[success_state.id].prob = hash_table[success_state.id].prob + success_state.prob  # Sum similar state probablity
            
            if hash_table[success_state.id].push_count == state.push_count: # Golden fix of push count
                # Add to push count of the state
                hash_table[success_state.id].push_count += 1
        
        else:
            hash_table[success_state.id] = success_state
            hash_table[success_state.id].push_count += 1
            # if flow_name != '':
            if tick_clock_flag:
                hash_table[success_state.id].tick_clock(tick_num)
                # tick_clock_flag = False
        
        hash_table[success_state.id].prob_cons = round(float(factor(hash_table[success_state.id].prob).subs(prob, const_prob)),3)
        # Last step of generating soccess state: 
        #   Adding the success state to the hash_table
        state.right = hash_table[success_state.id]
        
        
        # ------------------------------------
        # Create a new state for failure -----
        # if flow_name not in state.queue: # changed from: "if state.workload[flow_name] == True:" to "if flow_name not in state.queue:"
        if not any(flow_name[0] == f[0] for f in state.queue):
            return hash_table

        # Update flow failure count
        fail_state.queue[fail_state.queue.index(flow_name)][1] += 1

        # Updat probability
        fail_state.prob = fail_state.prob * (1-prob)
        fail_state.prob_cons = round(float(factor(fail_state.prob).subs(prob, const_prob)), 3)
        
        # Update unique id
        fail_state.update_id()
        
        # Update new hashtable with failure state
        hash_table[fail_state.id] = fail_state
        if tick_clock_flag:
            hash_table[fail_state.id].tick_clock(tick_num)
            # tick_clock_flag = False
        
        
        # Last step of generating failure state: 
        #   Adding the success state to the hash_table
        state.left = hash_table[fail_state.id]

        return hash_table
 
    
    def apply_drop(self, flow_name, tick_clock_flag, state, hash_table, prob=symbols('S'), tick_num=1, threshold=0, const_prob=0.8):
        
        
        if flow_name == '':
            state.tick_clock(tick_num)
            hash_table[state.id] = state
            return hash_table
        
        state.instruction = f'Drop ({flow_name})'
        
        
        # ------ Copy success_state --------
        success_state = copy.deepcopy(state)
        # ----------------------------------
        
        
        
        # ------------------------------------
        # Create a new state for success -----
        
        
        # if flow_name in state.queue: # changed from "if state.workload[flow_name] != True:" to "if flow_name in state.queue:"
        if any(flow_name == f for f in state.queue):
            # success_state.workload[flow_name] = True
            success_state.prob = success_state.prob  # Multiply S probability # changed from: success_state.prob * prob --to--> success_state.prob
            success_state.queue.pop(0)
        else:
            success_state.prob *= 1
        
        # Generate unique id
        success_state.update_id()
        
        # Update new hashtable with success state (Merge section)
        if success_state.id in hash_table:
            hash_table[success_state.id].prob = hash_table[success_state.id].prob + success_state.prob  # Sum similar state probablity
            
            if hash_table[success_state.id].push_count == state.push_count: # Golden fix of push count
                # Add to push count of the state
                hash_table[success_state.id].push_count += 1
        
        else:
            hash_table[success_state.id] = success_state
            hash_table[success_state.id].push_count += 0  # changed from 1 to 0
            # if flow_name != '':
            if tick_clock_flag:
                hash_table[success_state.id].tick_clock(tick_num)
                # tick_clock_flag = False
        
        hash_table[success_state.id].prob_cons = round(float(factor(hash_table[success_state.id].prob).subs(prob, const_prob)), 3)
        # Last step of generating soccess state: 
        #   Adding the success state to the hash_table
        state.right = hash_table[success_state.id]
        

        return hash_table
               

    def pull(self, flow_name, tick_clock_flag, hash_table, prob=symbols('S'), tick_num=1, threshold=0, const_prob=0.8):
        """Applying the pull function for all the states in the hash_table.
            Replacing each state with two new fork of it (Success and failure)
            by the follwoing order:
            
            * pop every state
            * multiply one by S and another by F
            * put the two new states in the new hash table
            * merge similar states
        """       
        # hash_table = {}
        
        for key in list(hash_table.keys()):
            state = hash_table.pop(key)
            self.archive[key] = state
            
            state_probability = round(state.prob.subs(prob, const_prob), 3)
            
            # Evaluate each state before forking
            path_eval_result = self.path_eval(state)[0]
            
            # Fork state only if the state path condition is satisfiable.
            if path_eval_result == 'sat':
                
                # If state's probability is less than the threshold, purge it.
                if state_probability <= threshold:
                    continue
                
                # If a flow name has been given, then pull the flow with the given name
                elif flow_name != '':
                    hash_table = self.apply_pull(flow_name, tick_clock_flag, state, hash_table, prob, tick_num, threshold, const_prob)
                    
                # If no flow name has been given, then pick one from the queue to pull (If there is one to pick)
                elif len(state.queue) > 0:
                    hash_table = self.apply_pull(state.queue[0], tick_clock_flag, state, hash_table, prob, tick_num, threshold, const_prob)

                # If no flow has been left in the queue then just go to sleep
                else:        
                    hash_table = self.single_sleep(tick_clock_flag=True, hash_table=hash_table, state=state, tick_num=1)
                            
        # Replacing the new hash table with the old one
        return hash_table

    
    def single_pull(self, state, flow_name, tick_clock_flag, hash_table, prob=symbols('S'), tick_num=1, threshold=0.2, failure_threshold=3, const_prob=0.8):
        """Apply a pull only on the given state

        Args:
            state (_type_): _description_
            flow_name (_type_): _description_
            tick_clock_flag (_type_): _description_
            hash_table (bool): _description_
            prob (_type_, optional): _description_. Defaults to symbols('S').
            tick_num (int, optional): _description_. Defaults to 1.
            threshold (float, optional): _description_. Defaults to 0.2.
            const_prob (float, optional): _description_. Defaults to 0.8.

        Returns:
            _type_: _description_
        """
        
        hash_table.pop(state.id)
        self.archive[state] = state
    
    
        # Evaluate each state before forking
        path_eval_result = self.path_eval(state)[0]
            
        # Fork state only if the state path condition is satisfiable.
        if path_eval_result == 'sat':
            
            
            
                
            # If a flow name has been given, then pull the flow with the given name
            if flow_name != '':
                hash_table = self.apply_pull(flow_name, tick_clock_flag, state, hash_table, prob, tick_num, threshold, const_prob)
            
            # If no flow name has been given, then pick one from the queue to pull (If there is one to pick)
            elif len(state.queue) > 0:
                if state.queue[0][1] >= failure_threshold: # changed from "if state.prob_cons <= threshold:" 
                    self.apply_drop(state.queue[0], tick_clock_flag, state, hash_table, prob, tick_num, threshold, const_prob)
                else:
                    hash_table = self.apply_pull(state.queue[0], tick_clock_flag, state, hash_table, prob, tick_num, threshold, const_prob)
            
            # If no flow has been left in the queue then just go to sleep
            else:
                hash_table = self.single_sleep(tick_clock_flag=True, hash_table=hash_table, state=state, tick_num=1)
        
        # Replacing the new hash table with the old one
        return hash_table


    def apply_c_split(self, condition_name, tick_clock_flag, state, hash_table, tick_num=1):
        """Apply a conditional fork on the given state and adding the two possible
        deterministic state to the given hash_table

        Args:
            condition_name (_type_): _description_
            tick_clock_flag (_type_): _description_
            state (_type_): _description_
            hash_table (bool): _description_
            tick_num (int, optional): _description_. Defaults to 1.

        Returns:
            _type_: _description_
        """
        
        
        if condition_name == '':
            state.tick_clock(tick_num)
            hash_table[state.id] = state
            return hash_table
        
        
        # -------- Copy fail_state --------
        fail_state = copy.deepcopy(state)
        # ---------------------------------
        
        # ------ Copy success_state --------
        success_state = copy.deepcopy(state)
        # ----------------------------------
        
        
        
        # ------------------------------------
        # Create a new state for success -----
        
        # Update workloads and probablity
        success_state.conditions.add(condition_name+"==0")
        if tick_clock_flag:
            hash_table[success_state.id].tick_clock(tick_num)
        
        # Remove sat model
        # success_state.model = ''
        
        # Generate unique id
        success_state.update_id()
        
        # add one to the split count
        success_state.split_count += 1
        
        # Update new hashtable with success state
        hash_table[success_state.id] = success_state
        
        path_eval_result = self.path_eval(success_state)
        # Add to right child of the old state
        state.right = hash_table[success_state.id]
        
        
        # ------------------------------------
        # Create a new state for failure -----

        # Updat probability
        # Update workloads and probablity
        fail_state.conditions.add(condition_name+"!=0")
        
        if tick_clock_flag:
            hash_table[fail_state.id].tick_clock(tick_num)
        
        # Remove sat model
        # fail_state.model = ''
        
        # Generate unique id
        fail_state.update_id()
        
        # Add one to the split count
        fail_state.split_count += 1
        
        # Update new hashtable with success state
        hash_table[fail_state.id] = fail_state

        path_eval_result = self.path_eval(fail_state)
        # Add to right child of the old state
        state.left = hash_table[fail_state.id]
        
        
        return hash_table
 
    
    def c_split(self, condition_name, tick_clock_flag, hash_table, tick_num=1):
        """Applying the conditional deterministic split function 
        for all the states in the hash_table and replacing each 
        state with two new fork of it (Success and failure) by
        the following order:
        
            * pop every state
            * multiply one by S and another by F
            * put the two new states in the new hash table
            * merge similar states
        """
        
        temp_hash_table= {}
        for key in list(hash_table.keys()):
            state = hash_table.pop(key)
            state.instruction = f'Condition Split({condition_name})'
            self.archive[key] = state
            
            # Evaluate each state before forking
            path_eval_result = self.path_eval(state)[0]
            
            # Fork state only if the state path condition is satisfiable.
            if path_eval_result == 'sat':
                temp_hash_table = self.apply_c_split(condition_name, tick_clock_flag, state, temp_hash_table, tick_num)
            
        # Replacing the new hash table with the old one
        return temp_hash_table

        
    def drop_flow(self, flow_name, tick_clock_flag, hash_table, tick_num=1):
        
        for key in list(hash_table.keys()):
            state = hash_table.pop(key)
            state.instruction = f'Drop'
            self.archive[key] = state
            
            # ------------------------------------
            # Create a new reduced state ---------
            reduced_state = copy.deepcopy(state)

            # Drop the flow name from the workload
            reduced_state.queue.pop(reduced_state.queue.index(flow_name)) # changed from "reduced_state.workload.pop(flow_name)" to "reduced_state.queue.pop(reduced_state.queue.index(flow_name))"
            reduced_state.update_id()
            
            # Update new hashtable with success state (Merge section)
            if reduced_state.id in hash_table:
                hash_table[reduced_state.id].prob = hash_table[reduced_state.id].prob + reduced_state.prob     # Sum similar state probablity

            else:
                hash_table[reduced_state.id] = reduced_state
                if tick_clock_flag:
                    reduced_state.tick_clock(tick_num)
                    # tick_clock_flag = False
            
            state.right = hash_table[reduced_state.id]
        
        return hash_table
            

    def add_sleep(self, tick_clock_flag, hash_table, tick_num=1):
        """Add a number of sleep (no operation) to 
        all states of the given hash_table

        Args:
            tick_clock_flag (_type_): _description_
            hash_table (bool): _description_
            tick_num (int, optional): _description_. Defaults to 1.

        Returns:
            _type_: _description_
        """
        
        for key in list(hash_table.keys()):
            state = hash_table.pop(key)
            state.instruction = f'Sleep({tick_num})'
            self.archive[key] = state
            
            # ------------------------------------
            # Create a new reduced state ---------
            slept_state = copy.deepcopy(state)

            
            slept_state.update_id()
            
            # Evaluate each state before forking
            path_eval_result = self.path_eval(state)[0]
                
            # Fork state only if the state path condition is satisfiable.
            if path_eval_result == 'sat':
                    
                # Update new hashtable with success state (Merge section)
                hash_table[slept_state.id] = slept_state
                
                if tick_clock_flag:
                    slept_state.tick_clock(tick_num)
                
                state.right = slept_state
            
        return hash_table
    
    
    def single_sleep(self, tick_clock_flag, hash_table, state, tick_num=1):
        """Add a number of sleep (no op) only to the  
        given state and add to the given hash_table

        Args:
            tick_clock_flag (_type_): _description_
            hash_table (bool): _description_
            state (_type_): _description_
            tick_num (int, optional): _description_. Defaults to 1.

        Returns:
            _type_: _description_
        """
        
        
        state.instruction = f'Sleep({tick_num})'
        
        # ------------------------------------
        # Create a new reduced state ---------
        slept_state = copy.deepcopy(state)
                                          
        slept_state.update_id()           
        
        # Evaluate each state before forking
        path_eval_result = self.path_eval(state)[0]
            
        # Fork state only if the state path condition is satisfiable.
        if path_eval_result == 'sat':
            
            # Update new hashtable with success state (Merge section)
            hash_table[slept_state.id] = slept_state

            if tick_clock_flag:
                slept_state.tick_clock(tick_num)
                # tick_clock_flag = False
                
            
            state.right = slept_state
        
        return hash_table
    

    def visualize_dag(self, file_name='Digraph' , path_trace=[]):
        """Visualize the graph of the simulator and
        save it with the given file name in the ./Output/Graphs/ directory

        Args:
            file_name (str, optional): _description_. Defaults to 'Digraph'.
            const_prob (float, optional): _description_. Defaults to 0.8.

        Returns:
            _type_: _description_
        """
        
        
        if not self.root:
            return False
        
        # Set the root of the simulator as the root to be explored
        root = self.root

        # Defining the file and format of the output graph
        # graph = Digraph(f'./Output/Graphs/{file_name}', format='pdf')
        graph = Digraph(f'./Output/Graphs/{file_name}')
        
        # Calling the helper function to draw the graph with the given parameters
        self.draw_nodes_and_edges(root, graph, path_trace)
        
        # Generate the graph and clean the redundent files
        graph.view(cleanup=True)
        return


    def draw_nodes_and_edges(self, root, graph, path_trace):
        """Helpper function for the visualize_dag function to generate
        every node accessible from the root

        Args:
            root (_type_): _description_
            graph (_type_): _description_
            const_prob (_type_): _description_
        """
        
        success_prob = symbols('S')
        visited = set()
        queue = deque([root])

        while queue:
            
            # pop one node from the queue to visit
            node = queue.popleft()
            
            if node not in visited:
                
                # Gathering node's info to use to set it's vizual atribute
                # prob_float = round(node.prob.subs(success_prob, const_prob), 3)
                prob_float = node.prob_cons
                probability = int(prob_float * 100)                
                
                # Set the vizual atribute of the node based on it's info
                
                
                if node.model == 'unsat':
                    fill_color = 'pink'
                    font_color = 'Black'
                    
                else:
                    fill_color = f'gray{probability}'
                                    
                    if probability <=51:
                        font_color = 'white'
                    else:
                        font_color = 'Black'
                
                for target_node in path_trace:
                    if target_node.id == node.id and str(target_node.prob) == str(node.prob):
                        fill_color = 'gold'
                        font_color = 'Black'
                
                
                    
                # Graph information and style for the report
                graph.node(repr(node), 
                           label='ID: '+str(node.id)+'\n'+
                        #    'Workload: '+str(node.get_workload_string())+'\n'
                           'Clock: '+str(node.clock)+'\n'
                           +'Queue: '+''.join(f'|{e}' for e in node.queue)+'\n'
                           +f'Release Count: {node.release_count}'+'\n'
                           +f'Push Count: {node.push_count}'+'\n'
                           +'Path_cons: '+str(node.path_cons).replace('&&', '&&\n')+'\n'
                           +'Sat model: '+str(node.model)+'\n'
                        #    +'Split Count: ' + str(node.split_count) +'\n'
                           +'Prob:'+str(factor(node.prob))+'\n'
                           +f'prob Cons(S=0.8): '+str(prob_float)+'\n',
                        #    +repr(node), 
                           style='filled', fillcolor=fill_color, fontcolor=font_color)
                
                
                # Add node to the visited nodes
                visited.add(node)
                
                # Add new nodes to the queue if there are any
                if node.left: # and node.left.prob.subs(success_prob, prob) != 0:
                    graph.edge(repr(node), repr(node.left), label=node.instruction+' [F]')
                    queue.append(node.left)

                if node.right: # and node.right.prob.subs(success_prob, prob) != 0:
                    graph.edge(repr(node), repr(node.right), label=node.instruction+' [S]')
                    queue.append(node.right)


    def imprint_hash_table(self, simulation_name, hash_table, const_prob=0.8):
        """
        Printout the hash table of the simulation into the stdout
        and save a log of it in the ./Output/hashtables/ directory
        """
        success_prob = symbols('S')
        
        # open a new file to write the log (or rewrite it to be used for the most recent run)
        open(f'./Output/hashtables/{simulation_name}.txt', 'w')
        
        print('='*50, '\n','Hash table:')
        
        for state in hash_table:
            log = '[ ] '+str(state)[:5]+ "..." +'\t|'+\
                  'Path Cons: '+hash_table.get(state).path_cons + '\t|'+\
                  'Prob(Symbo): '+str(factor(hash_table.get(state).prob))+ '\t|'+\
                  'Prob(Const): '+str(hash_table.get(state).prob_cons)+ '\t|'+\
                  'Queue: '+ ''.join(f'|{e}' for e in hash_table.get(state).queue)+'\t|'+\
                  'Release Count: '+ str(hash_table.get(state).release_count)+'\t|'+'\n'+\
                  'Push Count: '+ str(hash_table.get(state).push_count)+'\t|'+'\n'+\
                  'Sat Model: ' + str(hash_table.get(state).model) #+\
                  
                          
                #   'Conditions:'+ hash_table.get(state).conditions + '|'
            #hash_table.get(state))
        
            print(log)
            
            # Write (or rewrite) the log into the generated file
            with open(f'./Output/hashtables/{simulation_name}.txt', 'a+') as hash_table_file:
                hash_table_file.write(log)

        print('='*50)

   
    def archive_print(self):
        """
        A function to print the archive of all the states
        that has been created in the simulation
        """
        
        print('Archive root is:', self.root.id, self.root)
        print('Length of Archive is:', len(self.archive))
        for state in self.archive.values:
            print('Path Constraints: ',state.id, state.clock, state)
            
            if state.left:
                print('\tLeft ID: ',state.left.id, state.clock, state.left)
            
            if state.right:
                print('\tRight ID: ', state.right.id, state.clock, state.right)
            print('-'*50)

        
    def path_eval(self, state):
        """A function to evaluate the path constrain of a state
        with help of z3 to see if it is satisfiable or not and
        returns the result as: [sat/unsat, model]

        Args:
            state (_type_): _description_

        Returns:
            _type_: _description_
        """
        
        # If there is no path constraint then it is satisfiable
        if state.path_cons == "":
            return "sat"
        
        # Create an instance of z3 and call it sovler
        solver = z3.Solver()
        
        # set the initial variables
        time_var = ['t', 'R', 'S', 'a']
        variables = {}
        # wrkload_var = list(state.workload.keys()) # changed from this
        wrkload_var = list()                        # to this
        
        # Converting the workload variables of a state 
        # to valid python variabl so they can be evaluate
        
        for var_name in wrkload_var + time_var:
            locals()[var_name] = z3.Int(var_name)
            variables[var_name] = locals()[var_name]
            
        # Separate path constraint strings to with and operators
        constraints_string = state.path_cons.split(" && ")
        
        # Converting all constraint strings into valid python
        # variables and then adding to the solver instance
        for constraint_str in constraints_string:
            constraint = eval(constraint_str, globals(), locals())
            solver.add(constraint)
        
        # Evaluating the constraints
        result = solver.check()
        
        # Configuring the correct output based on the result
        if str(result) == 'sat':
            model = solver.model()
            model_dict = {}
            
            for decl in model:
                model_dict[str(decl)] = model[decl].as_long()
            
            # print('Variables: ', variables)
            # print(constraints_string ,"Sat =>", model_dict)
            state.model = model_dict
            
        else:
            model = 'unsat'
            # print(result, constraints_string)
            state.model = model

        # Returning the output
        return [str(result), state.model]

                        
    def test_of_correctness(self, hash_table, std_out=True):
        """
            A funciton to test the result of the simulation
            by summing up the probabilities.
        """
        
        sum_of_probabilities = 0
        for state in hash_table:
            sum_of_probabilities += hash_table.get(state).prob
        
        if factor(sum_of_probabilities) == 1:
            if std_out:
                print('Test of correctness result:', '\033[92m'+'Correct'+'\033[0m')
            return True
        else:
            if std_out:
                print('Test of correctness result:', '\033[91m'+'Failed'+'\033[0m')
            return False
        
        
    def test_of_correctenss2(self, hash_table, std_out=True):
        """Evaluating the correctness of the current state of hash_table
        based on the probabilities for all possible constraint paths

        Args:
            hash_table (bool): _description_
            std_out (bool, optional): _description_. Defaults to True.

        Returns:
            _type_: _description_
        """
        
        
        const_to_state_dict = {}
        for state in hash_table.values():
            if state.path_cons not in const_to_state_dict:
                const_to_state_dict[state.path_cons] = [state]
            else:
                const_to_state_dict[state.path_cons].append(state)
        
        number_of_pathconst = len(const_to_state_dict)
        sum_of_all_probabilities = 0
        
        for const in const_to_state_dict:
            if std_out:
                print("Path constraint: ", const)
                print('Path constraint solution: ', self.path_eval(const_to_state_dict.get(const)[0])[1])
                print('Number of state with the same condition: ',len(const_to_state_dict.get(const)))
                
            sum_of_probabilities = 0
            
            
            for state in const_to_state_dict.get(const):
                if std_out:
                    print(state.queue , '--Prob-->',state.prob.subs(symbols('S'), 0.8)) # changed from "print(state.get_workload_string() ," to "print(state.queue ,"
                    
                sum_of_probabilities += state.prob

            sum_of_all_probabilities += factor(sum_of_probabilities)

            if std_out:
                print('\n\n')
            
            
        final_result = factor(factor(sum_of_all_probabilities)/ number_of_pathconst)
        if factor(sum_of_all_probabilities)/ number_of_pathconst == 1:
            print('Test of correctness result:', '\033[92m'+'Correct'+'\033[0m')
            return 0
        else:
            print('Test of correctness result:', '\033[91m'+'Failed'+'\033[0m')
            print('final_result: (prob/count): ', final_result)
            return 1

    
    
    # ---------- ARRIVAL CURVE & SERVICE CURVE ----------------
    
    def find_largest_success(self, hash_table):
        """Search through all the nodes in the hash table and find the
        largest release count that is the same as successful push_count
        """
        largest_success = 0
        for node in hash_table.values():
            if node.release_count == node.push_count and node.release_count > largest_success:
                largest_success = node.release_count
        
        return largest_success
    
    
    def find_most_released_count(self, hash_table):
        
        most_release_count = 0
        time_model = '-1'
        for node in hash_table.values():
            if node.release_count > most_release_count and node.model != 'unsat':
                most_release_count = node.release_count
                time_model = node.model['t']
                
        return most_release_count, time_model
    
    
    def is_leaf(self, hash_table, node):
        if node.id in hash_table and node.clock == hash_table[node.id].clock:
            return True
        else:
            return False
    
    
    def most_release_count(self, hash_table):
        """Search through all the nodes in the hash table and find the
        largest release count 
        """
        
        for n in list(hash_table.keys()):
            if hash_table[n].model != 'unsat':
            
                first_node = hash_table[n]
                largest_release_count = first_node.release_count
                largest_release_clock = first_node.clock
                largest_release_model = first_node.model['t']
                largest_release_id = first_node.id
                break
            
        for node in hash_table.values():
            if node.model != 'unsat' and node.release_count > largest_release_count:
                largest_release_count = node.release_count
                largest_release_clock = node.clock
                largest_release_model = node.model['t']
                largest_release_id = node.id
                
        return largest_release_clock, largest_release_count, largest_release_model
    
    
    def least_push_count(self, hash_table, threashold):
        """Search through all the nodes in the hash table and find the
        least push counts which's probability is higher than a threashold
        """
        
        # for node in hash_table.values():
            # print(node, type(node))
            # print('**** Clock: ', node.clock, '-- model: ', node.model, '-- push count: ', node.push_count, '-- cons prob:', node.prob_cons)
        
        
        for n in list(hash_table.keys()):
            if hash_table[n].model != 'unsat' and\
                hash_table[n].prob_cons >= threashold:
                    
                least_node = hash_table[n]
                max_delta = least_node.release_count - least_node.push_count
                break
                
        for node in hash_table.values():
            delta = node.release_count - node.push_count
            if node.model != 'unsat' and\
                node.push_count < least_node.push_count and\
                    node.prob_cons >= threashold:
                
                least_node = node
        
        return least_node.clock, least_node.push_count, least_node.model
   
    
    def find_arrival_curve(self, hash_table, most_released_count, time_model):
        # Setting the target as the node with most release count
        
        visited = set()
        paths = []
        time_symbol = symbols('t')
        
        def dfs(node, path):
            ## Disregrading visited nodes
            if node in visited \
                or node.model == 'unsat' \
                or node.model['t']!= time_model:
                return
            
            visited.add(node)

            if node.release_count == most_released_count and self.is_leaf(hash_table, node):
                paths.append(path)
            
            else:
                if node.right:
                    dfs(node.right, path + [node.right])

                if node.left:
                    dfs(node.left, path + [node.left])

        dfs(self.root, [self.root])
        
        
        # print('Number of paths: ',len(paths))
        # print('Output of arrival curve:')
        # for path in paths:
        # for node in paths[0]:
        #     print(str(node.id)[:5], '-', node.release_count, '-', str(node.clock))
        # print('-'*50)
        # print('='*50)
        # return paths[0]
        
        arrival_curve = dict()
        for node in paths[0]:            
            arrival_curve[node.clock.subs(time_symbol, node.model['t'])] = node.release_count

        return arrival_curve


    def search_for_least_push_count(self, hash_table, cons_prob, threshold):
        """Search through all the nodes in the hash table and find the
        least push count that is above the threshold 
        """
        success_prob = symbols('S')
        least_push_count = hash_table[list(hash_table.keys())[0]].push_count
        least_push_clock = hash_table[list(hash_table.keys())[0]].clock
        for node in hash_table.values():
            if node.push_count < least_push_count and\
               node.prob_cons > threshold:
                   
                least_push_count = node.push_count
                least_push_clock = node.clock

        return least_push_clock, least_push_count


    # =========== UNDER CONSTRUCTION AREA =============
    
    def find_all_paths(self, hash_table, threshold, fail_count=2):
        print('Finding all paths')
        # Setting the target as the leaf nodes
        
        visited = set()
        paths = []
        success_prob = symbols('S')
        
        def dfs(node, path, failure=0):
            ## Disregrading visited nodes
            # if node in visited:
            #     return
            # visited.add(node)
            
            if node.model == 'unsat' or\
                node.prob_cons < threshold:          # Other ideas: #const_prob ** fail_count: # failure > fail_count or\
                return
            
            if self.is_leaf(hash_table, node): # and most_release_count == node.release_count:# == node.push_count:
                paths.append(path) 
                
            else:
                if node.left:
                    if node.left.prob_cons < node.prob_cons:
                        failure += 1
                    dfs(node.left, path + [node.left], failure)

                if node.right:
                    if node.right.prob_cons > node.prob_cons:
                        failure -= 1
                    dfs(node.right, path + [node.right], failure)

        dfs(self.root, [self.root])
        
        print('Number of paths: ',len(paths))
        # for path in paths:
        #     for node in path:
        #         print(str(node.id)[:5], '-', node.release_count, '-', str(node.clock))
        #     print('-'*50)
        return paths
    
    
    def all_paths_to_push_data(self, all_founded_paths):
        
        all_founded_paths_push_data = list()
        
        for path in all_founded_paths:
            data = list()
            for node in path:
                clock_push_info = (node.clock, node.push_count)
                if clock_push_info not in data:
                    data.append(clock_push_info)

            data = [y for x, y in data]
            all_founded_paths_push_data.append(list(data))
            
        print("All founded push data: ")
        counter = 0
        for data in all_founded_paths_push_data:
            counter += 1
            print(f"Path #{counter}:", data)
        
        return all_founded_paths_push_data    
            
    
    def least_path_push_data(self, all_founded_paths_push_data):
        least_founded_path_push_data = list()
        
        for i in range(len(all_founded_paths_push_data[0])):
            
            least_founded_path_push_data.append(all_founded_paths_push_data[0][i])
            
            for data in all_founded_paths_push_data:
                if data[i] < least_founded_path_push_data[i]:
                    least_founded_path_push_data[i] = data[i]
            
        return least_founded_path_push_data
            
    
      
    def paths_to_curves(self, hash_table, all_paths):
        
        time_symbol = symbols('t')
        all_curves = list()
        for path in all_paths:
            curve = dict()
            for node in path:        
                curve[node.clock] = node.push_count
                # print('Appending: ', (node.clock.subs(time_symbol, node.model['t']), node.release_count))

            if curve not in all_curves:
                all_curves.append(curve)
                
        return all_curves

    
    def plot_all_curves(self, hash_table, plot_name, const_prob=0.8, fail_count=2, threshold=0.2, t_subs=''):
        t = symbols('t')
        most_release_count, time_model = self.find_most_released_count(hash_table)
        all_paths = self.find_all_paths(hash_table, most_release_count, time_model, const_prob, fail_count, threshold)
        all_curves = self.paths_to_curves(hash_table, all_paths)
            
        # Plot all other curves
        for i, curve_dict in enumerate(all_curves):
            x_values, y_values = zip(*curve_dict.items())
            
            # Check for time symbol substitute
            if not t_subs:
                x_values = [str(value) for value in x_values]
            else:
                x_values = [value.subs(t, t_subs) for value in x_values]
            
            # Uncomment to separate lines
            # y_values = [val + i * 0.03 for val in y_values]  # Adjust the y-values to separate the lines
            # x_values = [val + i * 0.03 for val in x_values]  # Adjust the x-values to separate the lines
            
            plt.plot(x_values, y_values, marker='o')#, label=f'Path {i + 1}')
            

        #specify axis tick step sizes
        # plt.xticks(np.arange(0, max(x_values)+1, 1))
        plt.xticks(rotation=45)
        plt.yticks(np.arange(0, max(y_values)+1, 1))
        
        plt.title(f'All possible curves (Success Probability:{const_prob}, Threshold: {threshold}, faile_count: {fail_count})')
        plt.xlabel('Time')
        plt.ylabel('Transmitted packets')

        info_text = f"Number of curves: {len(all_curves)}"
        plt.text(0.5, 0.95, info_text, transform=plt.gcf().transFigure, fontsize=12, ha='center')
        # plt.legend()
        plt.savefig("./Output/Plots/"+plot_name+'_all_push_counts', dpi=300)
        # plt.clf()
        # plt.show()


    # =========== UNDER CONSTRUCTION AREA =============
    
    def plot_release_curve_2D(self, curve, plot_name, t_subs=''):
        # plot the arrival curve
        t = symbols('t')
        
        x_values, y_values = zip(*curve)
        
        # Check for time symbol substitute
        if not t_subs:
            x_values = [str(value) for value in x_values]
        else:
            x_values = [value.subs(t, t_subs) for value in x_values]
        
        # Plot it
        plt.plot(x_values, y_values, marker='s', label=f'Cumulative release count', markerfacecolor='k')
        
        #specify axis tick step sizes
        # plt.xticks(np.arange(min(x_values), max(x_values)+1, 1))
        # plt.xticks(rotation=45)
        plt.yticks(np.arange(0, max(y_values)+1, 1))
        
        # Plot's specifications
        # plt.title(plot_name)
        plt.legend()
        plt.grid()
        plt.xlabel("Time")
        plt.ylabel('Number of packets')
        # plt.savefig("./Output/Plots/"+plot_name+'_release_count'+'.pdf', format='pdf')
        plt.savefig("./Output/Plots/"+plot_name+'_release_count', dpi=300)
        # plt.show()
        # Clear plot for later use
        # plt.clf()
        
        
    def plot_release_curve_3D(self, data):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Extract x, y, and z values from the data
        x_values = [entry[0] for entry in data]
        y_values = [entry[1] for entry in data]
        z_values = [entry[2] for entry in data]

        # Create a mapping of unique y_values to numerical indices
        y_unique = list(y_values)
        y_indices = [y_unique.index(y) for y in y_values]
        
        ax.plot(x_values, y_indices, z_values, marker='o', color='r', linestyle='-', markersize=8)

        ax.set_xticks(np.arange(min(x_values), max(x_values)+1, 1))
        ax.set_yticks(np.arange(min(y_indices), max(y_indices)+1, 1))
        ax.set_zticks(np.arange(min(z_values), max(z_values)+1, 1))
        ax.set_yticklabels(y_values)  # Set tick labels to the actual y_values

        ax.set_xlabel('Time model')
        ax.set_ylabel('Time')
        ax.set_zlabel('Packet Released')

        plt.show()
    
        
    def plot_push_curve_2D(self, curve, plot_name, t_subs=''):
        # plot the arrival curve
        t = symbols('t')
        
        x_values, y_values = zip(*curve)
        
        # Check for time symbol substitute
        if not t_subs:
            x_values = [str(value) for value in x_values]
        else:
            x_values = [value.subs(t, t_subs) for value in x_values]
        
        # Plot it
        plt.plot(x_values, y_values, marker='s', label=f'Cumulative least push count', markerfacecolor='k')
        
        #specify axis tick step sizes
        # plt.xticks(np.arange(min(x_values), max(x_values)+1, 1))
        plt.xticks(rotation=45)
        # plt.yticks(np.arange(0, max(y_values)+1, 1))
        
        # Plot's specifications
        # plt.title(plot_name)
        plt.legend()
        # plt.grid()
        plt.xlabel("Time")
        plt.ylabel('Number of packets')
        # plt.savefig("./Output/Plots/"+plot_name+'_push_count'+'.pdf', format='pdf')
        plt.savefig("./Output/Plots/"+plot_name+'_push_count', dpi=300)
        # plt.show()
        # Clear plot for later use
        plt.clf()
            
            
    def get_arrival_curve(self, data, verbose=False):
        arrival_curve = list()
        
        # for each time duration (td: time duration)
        for td in range(0, len(data)):
            delta = list()
            if verbose: print('     Time Duration: ',td)
            
            # we calculate maximum delta for each data[i: i+td+1]
            for i in range(len(data)-td):
                segment = data[i: i+td+1]
                if verbose: print(f'data[{i}: {i+td+1}]', segment, '     max - min => ', max(segment) - min(segment))
                delta.append(max(segment) - min(segment))
                
            if verbose: print('         Max is: ', max(delta))
            arrival_curve.append((td, max(delta)))
            
        return arrival_curve


    def get_service_curve(self, data, verbose=False):
        service_curve = list()
        
        # for each time duration (td: time duration)
        for td in range(0, len(data)):
            delta = list()
            if verbose: print('     Time Duration: ',td)
            
            # we calculate maximum delta for each data[i: i+td+1]
            for i in range(len(data)-td):
                segment = data[i: i+td+1]
                if verbose: print(f'data[{i}: {i+td+1}]', segment, '     max - min => ', max(segment) - min(segment))
                delta.append(max(segment) - min(segment))
            
            if verbose: print('delta :', delta)
            if verbose: print('         Max is: ', min(delta))
            service_curve.append((td, min(delta)))
            
        return service_curve

   
    def plot_arrival_curve(self, service_curve, plot_name):
        x_values, y_values = zip(*service_curve)
        
        # Plot it
        plt.step(x_values, y_values, marker='o', label=f'Arrival Curve', markerfacecolor='k', where='pre')
        
        # Customization
        plt.xticks(np.arange(min(x_values), max(x_values)+1, 1))
        plt.yticks(np.arange(0, max(y_values)+1, 1))
        # plt.title(plot_name)
        plt.xlabel("Time Duration") #Δ
        plt.ylabel('Number of packets')
        plt.grid()
        plt.legend()
        # plt.show()
        # plt.savefig("./Output/Plots/"+plot_name+'_arrival_curve'+'.pdf', format="pdf")
        plt.savefig("./Output/Plots/"+plot_name+'_arrival_curve', dpi=300)
        # plt.clf()
        
    
    def plot_service_curve(self, service_curve, plot_name, curve_name):
        x_values, y_values = zip(*service_curve)
        
        # Customization
        
        x_values = [val - 1 * 0.05 for val in x_values]  # Adjust the x-values to separate the lines
        y_values = [val + 1 * 0.05 for val in y_values]  # Adjust the y-values to separate the lines
            
        
        # Plot it
        plt.plot(x_values, y_values, marker='s', label=curve_name, markerfacecolor='k')#, where='pre')
        
        plt.xticks(np.arange(ceil(min(x_values)), ceil(max(x_values))+1, 1))
        plt.yticks(np.arange(0, max(y_values)+1, 1))
        # plt.title(plot_name)
        plt.xlabel("Time Duration") #Δ
        plt.ylabel('Number of packets')
        # plt.grid()
        plt.legend()
        # plt.show()
        # plt.savefig("./Output/Plots/"+plot_name+'_service_curve'+'.pdf', format="pdf")
        plt.savefig("./Output/Plots/"+plot_name+'_service_curve', dpi=300)
        # plt.clf()
    
