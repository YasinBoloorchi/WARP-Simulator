from graphviz import Digraph, Graph
from time import sleep
from sympy import symbols, factor, Integer
import copy
from collections import deque

class State:
    def __init__(self, workload={}):
        self.workload = workload
        self.prob = Integer(1)
        self.id = ''
        self.right = None
        self.left = None
        self.clock= 0
        
    def tick_clock(self):
        self.clock += 1

    def update_id(self):
        dictionary_keys = list(self.workload.keys())
        dictionary_keys.sort()
        sorted_dictionary = {key: self.workload[key] for key in dictionary_keys}
        key_value_strings = [f"{key}:{value}" for key, value in sorted_dictionary.items()]
        unique_string = ','.join(key_value_strings)
        
        self.id = unique_string
        return unique_string


class StatesCollection:
    def __init__(self):
        self.hash_table = {}
        self.archive = []
        self.root = State()
        self.root.id = 'root'
        # Hash table: {
                        # F0AC:True,F0BA:True 0.922 <Simulator.State object at 0x7f95e511a410>
                        # F0AC:False,F0BA:True 0.038 <Simulator.State object at 0x7f95e511a470>
                        # F0AC:True,F0BA:False 0.038 <Simulator.State object at 0x7f95e511a4d0>
                        # F0AC:False,F0BA:False 0.002 <Simulator.State object at 0x7f95e511a530>
                    #  } 


    def release(self, flow_name, tick_clock_flag=False):
        # flow_name = 'F0BA'    
        """Add the given flow_name with False status
        to all the states' workloads in the hash table
        """
        
        if not self.hash_table:
            self.hash_table[self.root.id] = self.root

        new_hash_table = {}
        
        for key in list(self.hash_table.keys()):
            
            state = self.hash_table.pop(key)
            new_state = copy.deepcopy(state)
            new_state.workload[flow_name] = False
            new_state.update_id()
            new_hash_table[new_state.id] = new_state
            
            if tick_clock_flag:
                new_state.tick_clock()
            
            state.right = new_hash_table[new_state.id]
            
        self.hash_table = new_hash_table.copy()
        return

    
    def apply_pull(self, flow_name, tick_clock_flag, state, new_hash_table, prob=symbols('S')):
        if flow_name == '':
            state.tick_clock()
            new_hash_table[state.id] = state
            return new_hash_table
        
        # -------- Copy fail_state --------
        fail_state = copy.deepcopy(state)
        # ---------------------------------
        
        # ------ Copy success_state --------
        success_state = copy.deepcopy(state)
        # ----------------------------------
        
        # ------------------------------------
        # Create a new state for success -----

        # Update workloads and probablity
        if state.workload[flow_name] != True:
            success_state.workload[flow_name] = True
            success_state.prob = success_state.prob * prob               # Multiply S probability
        else:
            success_state.prob *= 1
        
        # Generate unique id
        success_state.update_id()
        
        # Update new hashtable with success state (Merge section)
        if success_state.id in new_hash_table:
            new_hash_table[success_state.id].prob = new_hash_table[success_state.id].prob + success_state.prob  # Sum similar state probablity

        else:
            new_hash_table[success_state.id] = success_state
            if flow_name != '':
                if tick_clock_flag:
                    new_hash_table[success_state.id].tick_clock()
                    # tick_clock_flag = False
                
        
        state.right = new_hash_table[success_state.id]
        
        # ------------------------------------
        # Create a new state for failure -----
        if state.workload[flow_name] == True:
            return new_hash_table

        # Updat probability

        fail_state.prob = fail_state.prob * (1-prob)
        
        # Update unique id
        fail_state.update_id()
        
        # Update new hashtable with failure state
        new_hash_table[fail_state.id] = fail_state
        if tick_clock_flag:
            new_hash_table[fail_state.id].tick_clock()
            # tick_clock_flag = False
        
        state.left = new_hash_table[fail_state.id]

        return new_hash_table
    
    def pull(self, flow_name, tick_clock_flag, prob=symbols('S')):
        # flow_name = 'F0BA',
        # prob = 0.8
        
        """ * pop every state
            * multiply one by S and another by F
            * put the two new states in the new hash table
            * merge similar states
        """       
        new_hash_table = {}
        # new_hash_table = {}
        
        for key in list(self.hash_table.keys()):
            state = self.hash_table.pop(key)
            self.archive.append(state)
        
            new_hash_table = self.apply_pull(flow_name, tick_clock_flag, state, new_hash_table, prob)
            
        # Replacing the new hash table with the old one
        self.hash_table = new_hash_table.copy()
    
    
    def condition(self, condition, condition_is_true, condition_is_false, tick_clock_flag, prob=symbols('S')):
        new_hash_table = {}
        
        for key in list(self.hash_table.keys()):
            state = self.hash_table.pop(key)
            self.archive.append(state)
            
            # Checking the main condition
            # vvvvvvvvvvvvvvvvvvvvvvvvvvv
            # !has F0AB == Ture
            if not state.workload.get(condition): 
                
                
                
                
                # If it's pull command:
                flow_name = condition_is_true[1]+condition_is_true[2]
                new_hash_table = self.apply_pull(flow_name, tick_clock_flag, state, new_hash_table, prob)
            
            # Checking the main condition
            # vvvvvvvvvvvvvvvvvvvvvvvvvvv
            # !has F0AB == False
            else:                     
                
                
                
                
                # If it's pull command
                flow_name = condition_is_false[1]+condition_is_false[2]
                new_hash_table = self.apply_pull(flow_name, tick_clock_flag, state, new_hash_table, prob)
                
        # Replacing the new hash table with the old one
        self.hash_table = new_hash_table.copy()
        
        
    def drop_flow(self, flow_name, tick_clock_flag):
        new_hash_table = {}
        
        for key in list(self.hash_table.keys()):
            state = self.hash_table.pop(key)
            self.archive.append(state)
            
            # ------------------------------------
            # Create a new reduced state ---------
            reduced_state = copy.deepcopy(state)

            # Drop the flow name from the workload
            reduced_state.workload.pop(flow_name)
            reduced_state.update_id()
            
            # Update new hashtable with success state (Merge section)
            if reduced_state.id in new_hash_table:
                new_hash_table[reduced_state.id].prob = new_hash_table[reduced_state.id].prob + reduced_state.prob     # Sum similar state probablity

            else:
                new_hash_table[reduced_state.id] = reduced_state
                if tick_clock_flag:
                    reduced_state.tick_clock()
                    # tick_clock_flag = False
            
            state.right = new_hash_table[reduced_state.id]
        
        self.hash_table = new_hash_table
            

    def add_sleep(self, tick_clock_flag):
        new_hash_table = {}
        
        for key in list(self.hash_table.keys()):
            state = self.hash_table.pop(key)
            self.archive.append(state)
            
            # ------------------------------------
            # Create a new reduced state ---------
            slept_state = copy.deepcopy(state)
            

            
            slept_state.update_id()
            # Update new hashtable with success state (Merge section)
            new_hash_table[slept_state.id] = slept_state
            
            if tick_clock_flag:
                slept_state.tick_clock()
                # tick_clock_flag = False
                
            
            state.right = slept_state
        
        self.hash_table = new_hash_table
    

    def visualize_dag(self, file_name='Digraph' ,prob=0.8):
        if not self.root:
            return False
        
        # self.root = self.archive[0]

        graph = Digraph(f'./Output/{file_name}', format='png')
        self.add_nodes_and_edges(graph, prob)
        
        graph.view()
        
        return


    def add_nodes_and_edges(self, graph, prob):
        success_prob = symbols('S')
        visited = set()
        queue = deque([self.root])

        while queue:
            node = queue.popleft()

            if node not in visited:
                graph.node(repr(node), 
                           label='ID: '+str(node.id)+'\n'
                           +'Prob:'+str(factor(node.prob))+'\n'
                           +f'prob (S={prob}): '+str(round(node.prob.subs(success_prob, prob), 3))+'\n'
                           +'Clock: '+str(node.clock)+'\n'
                           +repr(node))
                
                visited.add(node)

                if node.left:
                    graph.edge(repr(node), repr(node.left), label='F')
                    queue.append(node.left)

                if node.right:
                    graph.edge(repr(node), repr(node.right), label='S')
                    queue.append(node.right)

