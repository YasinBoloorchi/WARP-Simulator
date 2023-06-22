from graphviz import Digraph, Graph
from Parser import inst_parser
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


class Simulator:
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


    def run_slot(self, slot, hash_table={}):
        if hash_table == {}:
            hash_table = self.hash_table
        
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
                hash_table = self.add_sleep(tick_clock_flag)
              
                
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

            self.hash_table = hash_table.copy()
        
        return hash_table


    def release(self, flow_name, hash_table, tick_clock_flag=False):
        # flow_name = 'F0BA'    
        """Add the given flow_name with False status
        to all the states' workloads in the hash table
        """
        
        if not hash_table:
            hash_table[self.root.id] = self.root

        
        for key in list(hash_table.keys()):
            
            state = hash_table.pop(key)
            new_state = copy.deepcopy(state)
            new_state.workload[flow_name] = False
            new_state.update_id()
            hash_table[new_state.id] = new_state
            
            if tick_clock_flag:
                new_state.tick_clock()
            
            state.right = hash_table[new_state.id]
            
        return hash_table

    
    def apply_pull(self, flow_name, tick_clock_flag, state, hash_table, prob=symbols('S')):
        if flow_name == '':
            state.tick_clock()
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
        if state.workload[flow_name] != True:
            success_state.workload[flow_name] = True
            success_state.prob = success_state.prob * prob               # Multiply S probability
        else:
            success_state.prob *= 1
        
        # Generate unique id
        success_state.update_id()
        
        # Update new hashtable with success state (Merge section)
        if success_state.id in hash_table:
            hash_table[success_state.id].prob = hash_table[success_state.id].prob + success_state.prob  # Sum similar state probablity

        else:
            hash_table[success_state.id] = success_state
            if flow_name != '':
                if tick_clock_flag:
                    hash_table[success_state.id].tick_clock()
                    # tick_clock_flag = False
                
        
        state.right = hash_table[success_state.id]
        
        # ------------------------------------
        # Create a new state for failure -----
        if state.workload[flow_name] == True:
            return hash_table

        # Updat probability

        fail_state.prob = fail_state.prob * (1-prob)
        
        # Update unique id
        fail_state.update_id()
        
        # Update new hashtable with failure state
        hash_table[fail_state.id] = fail_state
        if tick_clock_flag:
            hash_table[fail_state.id].tick_clock()
            # tick_clock_flag = False
        
        state.left = hash_table[fail_state.id]

        return hash_table
 
    
    def pull(self, flow_name, tick_clock_flag, hash_table, prob=symbols('S')):
        # flow_name = 'F0BA',
        # prob = 0.8
        
        """ * pop every state
            * multiply one by S and another by F
            * put the two new states in the new hash table
            * merge similar states
        """       
        # hash_table = {}
        
        for key in list(hash_table.keys()):
            state = hash_table.pop(key)
            self.archive.append(state)
        
            temp_hash_table = self.apply_pull(flow_name, tick_clock_flag, state, hash_table, prob)
            
        # Replacing the new hash table with the old one
        return temp_hash_table
    
    
    def condition(self, condition_type, condition, condition_is_true_inst, condition_is_false_inst, tick_clock_flag, hash_table, prob=symbols('S')):
        
        def check_if_condition(state, condition_type, condition):
            
            if condition_type == '!has':
                if not state.workload.get(condition):
                    return True
                else:
                    return False
                
            # elif condition_type == 'has':
            #     if state.workload.get(condition):
            #         return True
            #     else:
            #         return False
            
        
        condition_is_true_hash_table = {}
        condition_is_false_hash_table = {}
        
        for key in list(hash_table.keys()):
            state = hash_table.pop(key)
            self.archive.append(state)

            if check_if_condition(state, condition_type, condition):
                
                condition_is_true_hash_table[key] = state
                
            else:
                
                condition_is_false_hash_table[key] = state
        
        
        condition_is_true_hash_table = self.run_slot(condition_is_true_inst, condition_is_true_hash_table)
        
        if condition_is_false_inst:
            condition_is_false_hash_table = self.run_slot(condition_is_false_inst, condition_is_false_hash_table)


        hash_table = condition_is_true_hash_table
        
        for key in list(condition_is_false_hash_table.keys()):
            if key in hash_table:
                # hash_table[success_state.id].prob = hash_table[success_state.id].prob + success_state.prob  # Sum similar state probablity
                
                hash_table[key].prob += condition_is_false_hash_table.get(key).prob
                
                condition_is_false_hash_table.get(key).right = hash_table[key]  # Sum similar state probablity
                
            else:
                hash_table[key] = condition_is_false_hash_table.pop(key)
            
        # print(hash_table)
        
        
        return hash_table
    
        
        for key in list(hash_table.keys()):
            state = hash_table.pop(key)
            self.archive.append(state)
            
            # Checking the main condition
            # vvvvvvvvvvvvvvvvvvvvvvvvvvv
            # !has F0AB == Ture
            if not state.workload.get(condition): 
                
                
                
                
                # If it's pull command:
                flow_name = condition_is_true[1]+condition_is_true[2]
                temp_hash_table = self.apply_pull(flow_name, tick_clock_flag, state, hash_table, prob)

            # Checking the main condition
            # vvvvvvvvvvvvvvvvvvvvvvvvvvv
            # !has F0AB == False
            else:                     
                
                
                
                
                # If it's pull command
                flow_name = condition_is_false[1]+condition_is_false[2]
                temp_hash_table = self.apply_pull(flow_name, tick_clock_flag, state, hash_table, prob)
                
        # Replacing the new hash table with the old one
        return temp_hash_table.copy()
        
        
    def drop_flow(self, flow_name, tick_clock_flag, hash_table):
        
        for key in list(hash_table.keys()):
            state = hash_table.pop(key)
            self.archive.append(state)
            
            # ------------------------------------
            # Create a new reduced state ---------
            reduced_state = copy.deepcopy(state)

            # Drop the flow name from the workload
            reduced_state.workload.pop(flow_name)
            reduced_state.update_id()
            
            # Update new hashtable with success state (Merge section)
            if reduced_state.id in hash_table:
                hash_table[reduced_state.id].prob = hash_table[reduced_state.id].prob + reduced_state.prob     # Sum similar state probablity

            else:
                hash_table[reduced_state.id] = reduced_state
                if tick_clock_flag:
                    reduced_state.tick_clock()
                    # tick_clock_flag = False
            
            state.right = hash_table[reduced_state.id]
        
        return hash_table
            

    def add_sleep(self, tick_clock_flag, hash_table):
        
        for key in list(hash_table.keys()):
            state = hash_table.pop(key)
            self.archive.append(state)
            
            # ------------------------------------
            # Create a new reduced state ---------
            slept_state = copy.deepcopy(state)
            

            
            slept_state.update_id()
            # Update new hashtable with success state (Merge section)
            hash_table[slept_state.id] = slept_state
            
            if tick_clock_flag:
                slept_state.tick_clock()
                # tick_clock_flag = False
                
            
            state.right = slept_state
        
        return hash_table
    

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

                if node.left: # and node.left.prob.subs(success_prob, prob) != 0:
                    graph.edge(repr(node), repr(node.left), label='F')
                    queue.append(node.left)

                if node.right: # and node.right.prob.subs(success_prob, prob) != 0:
                    graph.edge(repr(node), repr(node.right), label='S')
                    queue.append(node.right)


    def imprint_hash_table(self):
        """
        Printout the hash table of the simulation
        """
        print('Hash table:')
        success_prob = symbols('S')
        for state in self.hash_table:
            print('\t',state, '|',
                  self.hash_table.get(state).workload,'|',
                  factor(self.hash_table.get(state).prob), '|',
                  round(factor(self.hash_table.get(state).prob).subs(success_prob, 0.8), 3), '|',
                  self.hash_table.get(state))
    
   
    def archive_print(self):
        """
        A function to print the archive of all the states
        that has been created in the simulation
        """
        
        print('Archive root is:', self.root.id, self.root)
        print('Length of Archive is:', len(self.archive))
        for state in self.archive:
            print('ID: ',state.id, state.clock, state)
            
            if state.left:
                print('\tLeft ID: ',state.left.id, state.clock, state.left)
            
            if state.right:
                print('\tRight ID: ', state.right.id, state.clock, state.right)
            print('-'*50)
            
            
    def test_of_correctness(self):
        """
            A funciton to test the result of the simulation
            by summing up the probabilities.
        """
        
        sum_of_probabilities = 0
        for state in self.hash_table:
            sum_of_probabilities += self.hash_table.get(state).prob
        
        if factor(sum_of_probabilities) == 1:
            return '\033[92m'+'Correct'+'\033[0m'
        else:
            return '\033[91m'+'Failed'+'\033[0m'