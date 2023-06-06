from graphviz import Graph
from time import sleep
from sympy import symbols, factor
import copy


class State:
    def __init__(self, prob=1, workload={},):
        self.prob = prob
        self.workload = workload
        self.id = ''

class StatesCollection:
    def __init__(self):
        self.hash_table = {}
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
        

    def release(self, flow_name):
        # flow_name = 'F0BA'    
        
        """Add the given flow_name with False status
        to all the states' workloads in the hash table
        """
        
        if not self.hash_table:
            initial_state = State(prob=1, workload={flow_name:False})
            initial_state.id = self.generate_unique_string(initial_state.workload)
            self.hash_table[initial_state.id] = initial_state
            return


        new_hash_table = {}
        
        for key in list(self.hash_table.keys()):
            
            state = self.hash_table.pop(key)
            state.workload[flow_name] = False
            state.id = self.generate_unique_string(state.workload)

            new_hash_table[state.id] = state
            
        self.hash_table = new_hash_table.copy()

    
    def pull(self, flow_name, prob=symbols('S')):
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
            
            # ------------------------------------
            # Create a new state for success -----
            success_state = copy.deepcopy(state)
            
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
            
            # ------------------------------------
            # Create a new state for failure -----
            if state.workload[flow_name] == True:
                continue
            
            fail_state = copy.deepcopy(state)
            
            # Updat probability

            fail_state.prob = fail_state.prob * (1-prob)
            
            # Update unique id
            fail_state.id = self.generate_unique_string(fail_state.workload)
            
            # Update new hashtable with failure state
            new_hash_table[fail_state.id] = fail_state
        
        # Replacing the new hash table with the old one
        self.hash_table = new_hash_table.copy()
    
    
    def conditional_pull(self, condition, condition_is_true, condition_is_false, prob=symbols('S')):
        decimal_precision = 3
        new_hash_table = {}
        
        print('Hash table before conditional pull:')
        for state in self.hash_table:
            print('\t',state, '|',self.hash_table.get(state).prob, '|',self.hash_table.get(state))
        
        for key in list(self.hash_table.keys()):
            state = self.hash_table.pop(key)
            
            # Checking the main condition
            if not state.workload.get(condition): # !has F0AB == Ture
                flow_name = condition_is_true
                # ------------------------------------
                # Create a new state for success -----
                success_state = copy.deepcopy(state)
                
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
                
                # ------------------------------------
                # Create a new state for failure -----
                if state.workload[flow_name] == True:
                    continue
                
                fail_state = copy.deepcopy(state)
                
                # Updat probability

                fail_state.prob = fail_state.prob * (1-prob)
                
                # Update unique id
                fail_state.id = self.generate_unique_string(fail_state.workload)
                
                # Update new hashtable with failure state
                new_hash_table[fail_state.id] = fail_state
                
                    
            else: # !has F0AB == False
                flow_name = condition_is_false
                
                if condition_is_false == '':
                    new_hash_table[state.id] = state
                    continue
                
                # ------------------------------------
                # Create a new state for success -----
                success_state = copy.deepcopy(state)
                
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
                
                # ------------------------------------
                # Create a new state for failure -----
                if state.workload[flow_name] == True:
                    continue
                
                fail_state = copy.deepcopy(state)
                
                # Updat probability

                fail_state.prob = fail_state.prob * (1-prob)
                
                # Update unique id
                fail_state.id = self.generate_unique_string(fail_state.workload)
                
                # Update new hashtable with failure state
                new_hash_table[fail_state.id] = fail_state
                

        # Replacing the new hash table with the old one
        self.hash_table = new_hash_table.copy()
        
    
    def drop_flow(self, flow_name):
        decimal_precision = 3
        new_hash_table = {}
        
        for key in list(self.hash_table.keys()):
            state = self.hash_table.pop(key)
            
            # Drop the flow name from the workload
            state.workload.pop(flow_name)
            state.id = self.generate_unique_string(state.workload)
            
            # Update new hashtable with success state (Merge section)
            if state.id in new_hash_table:

                new_hash_table[state.id].prob = new_hash_table[state.id].prob + state.prob     # Sum similar state probablity

            else:
                new_hash_table[state.id] = state
            
        
        self.hash_table = new_hash_table
            
    
    def visualize(self):
        if not self.hash_table:
            print('Hash table is empty')
            return        

        graph = Graph('./Output/Simulators_output', format='png')
        
        for key in self.hash_table:
            state = self.hash_table.get(key)
            graph.node(state.id, label=state.id+'\n'+str(state.prob))
            
        graph.view()
    

