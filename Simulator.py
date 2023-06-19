from graphviz import Digraph, Graph
from Parser import parse_instructions, inst_parser
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


    def run_slot(self, slot, new_hash_table={}):
        pull_count = 0
        tick_clock_flag = True
        keep_clock_flag = False
        for inst in slot:
            inst_type = inst[0]
            instruction = inst[1]
            print('\n\n[Inst] ',inst, '| inst type: ', inst_type, '| instruction: ', instruction)
            
            if inst_type == 'release':
                parsed_instruction = inst_parser(instruction)[0]
                # inst_parser => [('release', 'F0', 'BA', '')]
            
                flow_name = parsed_instruction[1]+parsed_instruction[2]
                
                # workload[flow_name] = {'source': address[0], 'dest':address[1], 'has':False}
                
                new_hash_table = self.release(flow_name, new_hash_table, tick_clock_flag)
                
            
            elif inst_type == 'drop':
                parsed_instruction = inst_parser(instruction)[0]
                # inst_parser => [('drop', 'F0', 'BA', '')] 
                
                flow_name = parsed_instruction[1]+parsed_instruction[2]
                
                new_hash_table = self.drop_flow(flow_name, tick_clock_flag, new_hash_table)


            elif inst_type == 'pull' or inst_type == 'push':
                pull_count += 1
                parsed_instruction = inst_parser(instruction)
                # inst_parser => [('pull', 'F0', 'BA', '#0')] 
                
                instruc, flow_number, nodes, channel_number = parsed_instruction = inst_parser(instruction)[0]
                flow_name =flow_number + nodes
                new_hash_table = self.pull(flow_name, tick_clock_flag, new_hash_table)#, prob=0.8)
                
            
            elif inst_type == 'if':
                pull_count += 1
                parsed_instruction = inst_parser(instruction)
                # inst_parser => [('has', 'F0', 'BA', ''), ('pull', 'F0', 'BA', '#1'), ('pull', 'F0', 'AC', '#1')] 
                
                condition, condition_is_true, condition_is_false = inst_parser(instruction)         

                #          F0         pull(F0,#1)         pull (F1,#1)
                #         vvvv         vvvvvvvv              vvvv
                # print(condition, condition_is_true, condition_is_false)
                
                condition_flow_name = condition[1]+condition[2]
                
                
                new_hash_table = self.condition(condition_flow_name, condition_is_true, condition_is_false, tick_clock_flag, new_hash_table)#, prob=0.8)


            elif inst_type == 'sleep':
                # print(instruction)
                # self.add_sleep_state(inst='sleep')
                new_hash_table = self.add_sleep(tick_clock_flag)
                
            
            
            if pull_count > 1:
                raise Exception('Unexceptable number of pull/push requests in a single slot.')
            
            # if not keep_clock_flag:
            tick_clock_flag = False
                # keep_clock_flag = False

            self.hash_table = new_hash_table.copy()
            

    def release(self, flow_name, new_hash_table, tick_clock_flag=False):
        # flow_name = 'F0BA'    
        """Add the given flow_name with False status
        to all the states' workloads in the hash table
        """
        
        if not new_hash_table:
            new_hash_table[self.root.id] = self.root

        
        for key in list(new_hash_table.keys()):
            
            state = new_hash_table.pop(key)
            new_state = copy.deepcopy(state)
            new_state.workload[flow_name] = False
            new_state.update_id()
            new_hash_table[new_state.id] = new_state
            
            if tick_clock_flag:
                new_state.tick_clock()
            
            state.right = new_hash_table[new_state.id]
            
        return new_hash_table

    
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
 
    
    def pull(self, flow_name, tick_clock_flag, new_hash_table, prob=symbols('S')):
        # flow_name = 'F0BA',
        # prob = 0.8
        
        """ * pop every state
            * multiply one by S and another by F
            * put the two new states in the new hash table
            * merge similar states
        """       
        # new_hash_table = {}
        
        for key in list(new_hash_table.keys()):
            state = new_hash_table.pop(key)
            self.archive.append(state)
        
            temp_hash_table = self.apply_pull(flow_name, tick_clock_flag, state, new_hash_table, prob)
            
        # Replacing the new hash table with the old one
        return temp_hash_table
    
    
    def condition(self, condition, condition_is_true, condition_is_false, tick_clock_flag, new_hash_table, prob=symbols('S')):
        
        for key in list(new_hash_table.keys()):
            state = new_hash_table.pop(key)
            self.archive.append(state)
            
            # Checking the main condition
            # vvvvvvvvvvvvvvvvvvvvvvvvvvv
            # !has F0AB == Ture
            if not state.workload.get(condition): 
                
                
                
                
                # If it's pull command:
                flow_name = condition_is_true[1]+condition_is_true[2]
                temp_hash_table = self.apply_pull(flow_name, tick_clock_flag, state, new_hash_table, prob)
            
            # Checking the main condition
            # vvvvvvvvvvvvvvvvvvvvvvvvvvv
            # !has F0AB == False
            else:                     
                
                
                
                
                # If it's pull command
                flow_name = condition_is_false[1]+condition_is_false[2]
                temp_hash_table = self.apply_pull(flow_name, tick_clock_flag, state, new_hash_table, prob)
                
        # Replacing the new hash table with the old one
        return temp_hash_table.copy()
        
        
    def drop_flow(self, flow_name, tick_clock_flag, new_hash_table):
        
        for key in list(new_hash_table.keys()):
            state = new_hash_table.pop(key)
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
        
        return new_hash_table
            

    def add_sleep(self, tick_clock_flag, new_hash_table):
        
        for key in list(new_hash_table.keys()):
            state = new_hash_table.pop(key)
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
        
        return new_hash_table
    

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

