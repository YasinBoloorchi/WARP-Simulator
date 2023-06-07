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


class StatesCollection:
    def __init__(self):
        self.hash_table = {}
        # self.archive = []
        self.root = None
        # Hash table: {
                        # F0AC:True,F0BA:True 0.922 <Simulator.State object at 0x7f95e511a410>
                        # F0AC:False,F0BA:True 0.038 <Simulator.State object at 0x7f95e511a470>
                        # F0AC:True,F0BA:False 0.038 <Simulator.State object at 0x7f95e511a4d0>
                        # F0AC:False,F0BA:False 0.002 <Simulator.State object at 0x7f95e511a530>
                    #  } 
    
    def generate_unique_string(self, dictionary):
        dictionary_keys = list(dictionary.keys())
        dictionary_keys.sort()
        sorted_dictionary = {key: dictionary[key] for key in dictionary_keys}
        key_value_strings = [f"{key}:{value}" for key, value in sorted_dictionary.items()]
        unique_string = ','.join(key_value_strings)
        return unique_string
        

    def release(self, flow_name, tick_clock_flag=False):
        # flow_name = 'F0BA'    
        """Add the given flow_name with False status
        to all the states' workloads in the hash table
        """
        
        if not self.hash_table:
            initial_state = State(workload={flow_name:False})
            initial_state.id = self.generate_unique_string(initial_state.workload)
            self.hash_table[initial_state.id] = initial_state
            # self.archive.append(initial_state) # it'll cause the side offect of lean(archive) +1
            self.root = initial_state
            return True


        new_hash_table = {}
        
        for key in list(self.hash_table.keys()):
            
            state = self.hash_table.pop(key)
            state.workload[flow_name] = False
            state.id = self.generate_unique_string(state.workload)
            
            if tick_clock_flag:
                state.tick_clock()
            
            new_hash_table[state.id] = state
            
        self.hash_table = new_hash_table.copy()
        return False

    
    def pull(self, flow_name, tick_clock_flag, prob=symbols('S')):
        # flow_name = 'F0BA',
        # prob = 0.8
        
        """ * pop every state
            * multiply one by S and another by F
            * put the two new states in the new hash table
            * merge similar states
        """       
        
        new_hash_table = {}
        decimal_precision = 3
        
        for key in list(self.hash_table.keys()):
            state = self.hash_table.pop(key)
            # self.archive.append(state)
            
            # -------- Copy fail_state --------
            fail_state = copy.deepcopy(state)
            # ---------------------------------
            
            # ------ Copy success_state --------
            success_state = copy.deepcopy(state)
            # ----------------------------------
            
            # ------------------------------------
            # Create a new state for success -----
            if tick_clock_flag:
                success_state.tick_clock()
                
            # Update workloads and probablity
            if state.workload[flow_name] != True:
                success_state.workload[flow_name] = True
                success_state.prob = success_state.prob * prob               # Multiply S probability
            else:
                success_state.prob *= 1
            
            # Generate unique id
            success_state.id = self.generate_unique_string(success_state.workload)
            
            # Update new hashtable with success state (Merge section)
            if success_state.id in new_hash_table:
                new_hash_table[success_state.id].prob = new_hash_table[success_state.id].prob + success_state.prob  # Sum similar state probablity
                
            else:
                new_hash_table[success_state.id] = success_state
            
            state.right = new_hash_table[success_state.id]
            # ------------------------------------
            # Create a new state for failure -----
            if state.workload[flow_name] == True:
                continue
            
            if tick_clock_flag:
                fail_state.tick_clock()
                
            # Updat probability

            fail_state.prob = fail_state.prob * (1-prob)
            fail_state.clock += 1
            # Update unique id
            fail_state.id = self.generate_unique_string(fail_state.workload)
            
            # Update new hashtable with failure state
            new_hash_table[fail_state.id] = fail_state
            state.left = new_hash_table[fail_state.id]
        # Replacing the new hash table with the old one
        self.hash_table = new_hash_table.copy()
    
    
    def conditional_pull(self, condition, condition_is_true, condition_is_false, tick_clock_flag, prob=symbols('S')):
        decimal_precision = 3
        new_hash_table = {}
        
        print('Hash table before conditional pull:')
        for state in self.hash_table:
            print('\t',state, '|',self.hash_table.get(state).prob, '|',self.hash_table.get(state))
        
        for key in list(self.hash_table.keys()):
            state = self.hash_table.pop(key)
            # self.archive.append(state)
            
            # Checking the main condition
            if not state.workload.get(condition): # !has F0AB == Ture
                flow_name = condition_is_true
                
                
                                
                # -------- Copy fail_state --------
                fail_state = copy.deepcopy(state)
                # ---------------------------------
                
                # ------ Copy success_state --------
                success_state = copy.deepcopy(state)
                # ----------------------------------
                
                # ------------------------------------
                # Create a new state for success -----
                if tick_clock_flag:
                    success_state.tick_clock()
                    
                # Update workloads and probablity
                if state.workload[flow_name] != True:
                    success_state.workload[flow_name] = True

                    success_state.prob = success_state.prob * prob               # Multiply S probability
                else:
                    success_state.prob *= 1
                
                # Generate unique id
                success_state.id = self.generate_unique_string(success_state.workload)
                
                # Update new hashtable with success state (Merge section)
                if success_state.id in new_hash_table:
                    new_hash_table[success_state.id].prob = new_hash_table[success_state.id].prob + success_state.prob  # Sum similar state probablity

                else:
                    new_hash_table[success_state.id] = success_state
                
                state.right = new_hash_table[success_state.id]
                
                # ------------------------------------
                # Create a new state for failure -----
                if state.workload[flow_name] == True:
                    continue

                if tick_clock_flag:
                    fail_state.tick_clock()
                    
                # Updat probability

                fail_state.prob = fail_state.prob * (1-prob)
                
                # Update unique id
                fail_state.id = self.generate_unique_string(fail_state.workload)
                
                # Update new hashtable with failure state
                new_hash_table[fail_state.id] = fail_state
                state.right = new_hash_table[fail_state.id]
                
                    
            else: # !has F0AB == False
                flow_name = condition_is_false
                
                if condition_is_false == '':
                    new_hash_table[state.id] = state
                    continue
                
                # -------- Copy fail_state --------
                fail_state = copy.deepcopy(state)
                # ---------------------------------
                
                # ------ Copy success_state --------
                success_state = copy.deepcopy(state)
                # ----------------------------------
                
                # ------------------------------------
                # Create a new state for success -----
                if tick_clock_flag:
                    success_state.tick_clock()
                    
                # Update workloads and probablity
                if state.workload[flow_name] != True:
                    success_state.workload[flow_name] = True

                    success_state.prob = success_state.prob * prob               # Multiply S probability
                else:
                    success_state.prob *= 1
                
                # Generate unique id
                success_state.id = self.generate_unique_string(success_state.workload)
                
                # Update new hashtable with success state (Merge section)
                if success_state.id in new_hash_table:

                    new_hash_table[success_state.id].prob = new_hash_table[success_state.id].prob + success_state.prob  # Sum similar state probablity

                else:
                    new_hash_table[success_state.id] = success_state
                
                new_hash_table[success_state.id]
                
                # ------------------------------------
                # Create a new state for failure -----
                if state.workload[flow_name] == True:
                    continue
                
                if tick_clock_flag:
                    fail_state.tick_clock()
                    
                # Updat probability

                fail_state.prob = fail_state.prob * (1-prob)
                
                # Update unique id
                fail_state.id = self.generate_unique_string(fail_state.workload)
                
                # Update new hashtable with failure state
                new_hash_table[fail_state.id] = fail_state
                new_hash_table[fail_state.id]

        # Replacing the new hash table with the old one
        self.hash_table = new_hash_table.copy()
        
    
    def drop_flow(self, flow_name, tick_clock_flag):
        new_hash_table = {}
        
        for key in list(self.hash_table.keys()):
            state = self.hash_table.pop(key)
            # self.archive.append(state)
            
            # ------------------------------------
            # Create a new reduced state ---------
            reduced_state = copy.deepcopy(state)
            
            if tick_clock_flag:
                reduced_state.tick_clock()
            
            # Drop the flow name from the workload
            reduced_state.workload.pop(flow_name)
            reduced_state.id = self.generate_unique_string(reduced_state.workload)
            
            # Update new hashtable with success state (Merge section)
            if reduced_state.id in new_hash_table:
                new_hash_table[reduced_state.id].prob = new_hash_table[reduced_state.id].prob + reduced_state.prob     # Sum similar state probablity

            else:
                new_hash_table[reduced_state.id] = reduced_state
            
            state.right = reduced_state
        
        self.hash_table = new_hash_table
            

    def add_sleep(self, tick_clock_flag):
        new_hash_table = {}
        
        for key in list(self.hash_table.keys()):
            state = self.hash_table.pop(key)
            # self.archive.append(state)
            
            # ------------------------------------
            # Create a new reduced state ---------
            slept_state = copy.deepcopy(state)
            
            if tick_clock_flag:
                slept_state.tick_clock()
            
            slept_state.id = self.generate_unique_string(slept_state.workload)
            # Update new hashtable with success state (Merge section)
            new_hash_table[slept_state.id] = slept_state
            
            state.right = slept_state
        
        self.hash_table = new_hash_table
    

    def visualize_dag(self, prob=0.8):
        if not self.root:
            return False
        
        # self.root = self.archive[0]

        graph = Digraph('./Output/Digraph', format='png')
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
                           +'Prob:'+str(node.prob)+'\n'
                           +str(round(node.prob.subs(success_prob, prob), 3))+'\n'
                           +repr(node))
                
                visited.add(node)

                if node.left:
                    graph.edge(repr(node), repr(node.left), label='L')
                    queue.append(node.left)

                if node.right:
                    graph.edge(repr(node), repr(node.right), label='R')
                    queue.append(node.right)

