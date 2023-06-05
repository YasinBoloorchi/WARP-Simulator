from graphviz import Graph
from time import sleep

class Node:
    def __init__(self, node_id, label=None):
        self.node_id = node_id
        self.label = label
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

class State:
    def __init__(self, status='S', left=None, right=None, middle=None, prob=1, workload={}, inst='', path = '', path_prob=1):
        self.status = status
        self.left = left
        self.right = right
        self.middle = middle
        self.prob = prob
        self.inst = inst
        self.workload = workload
        self.path = path
        self.path_prob = path_prob
        workload_hash = ''.join([ str(b)[0] for b in list(self.workload.values())])
        self.id = str(len(self.path))+workload_hash

class StatesTree:
    def __init__(self, root=None):
        self.root = root
        self.hash_table = {}
        
        # Hash table: {'{F0BA:True, F0AC:False}': <Graphgen.State object at 0x7fa7dbcde530>, 
        #              '{F0AC:False, F0BA:True}': <Graphgen.State object at 0x7fa7dbcddd20>,
        #              '2F': <Graphgen.State object at 0x7fa7dbcddd80>,
        #              '2T': <Graphgen.State object at 0x7fa7dbcdddb0>,
        #              '3F': <Graphgen.State object at 0x7fa7dbcddde0>,
        #              '3T': <Graphgen.State object at 0x7fa7dbcdde10>,}
    
    
    def generate_unique_string(dictionary):
        sorted_items = sorted(dictionary.items())  # Sort dictionary by keys
        key_value_strings = [f"{key}:{value}" for key, value in sorted_items]
        unique_string = ",".join(key_value_strings)
        return unique_string

        # table = {'F0BA': True, 'F0AC': False}
        # unique_string = generate_unique_string(table)
        # print(unique_string)

    
    def pull(self, flow_name, prob):
        
        
        
        pass
    
    
      
    
    # ================== old code ============================
    
    # Adding two states to all leaf after a pull 
    def add_pull_state(self, prob=1, flow_name='', inst='', path='', path_prob=1):
        if not self.root:
            self.root = State()
            return
        
        self._add_pull_state_helper(self.root, prob, flow_name, inst, path, path_prob)
      
    def _add_pull_state_helper(self, state, prob, flow_name, inst, path, path_prob):
        print('='*35)
        print('- Call _add_pull_state_helper')
        print('state.path: ', state.path)
        print('Flow name: ', flow_name)
        print(state.workload)
        # self.visualize_tree()
        # sleep(0.5)
        print(self.hash_table)
        rdigits = 3
        
        # Skiping sleep states for being added right and left nodes
        if state.middle:
                print('-- If state.middle ')
                self._add_pull_state_helper(state.middle, 
                prob, 
                flow_name, 
                inst=inst, 
                path=path+'H', 
                path_prob= state.path_prob)
        
        # If it's not a sleep state
        else:
            print('-- else (if NOT state.middle)')
            # If it doesn't have a left node
            if not state.left:
                # if it's not successful yet       
                if not state.workload[flow_name]:
                    print('--- if not state.left')
                    left_work_load = state.workload.copy()
                    left_work_load[flow_name] = False
                    left_state = State(status='F', 
                                    prob=round(1-prob, rdigits), 
                                    workload=left_work_load, 
                                    inst=inst, 
                                    path=path+'F', 
                                    path_prob=round(state.path_prob*round(1-prob, rdigits), rdigits))  #main line for pull - for left node (failed attempt)
                    
                    print("--- left_state.id: ", left_state.id)
                
                    if  left_state.id in self.hash_table:
                        print('---- left_state.id in self.hash_table')
                        self.hash_table[left_state.id].path_prob += left_state.path_prob
                        state.left = self.hash_table[left_state.id]
                        return
                    
                    else:
                        print('---- else (left_state.id NOT in self.hash_table)')
                        state.left = left_state
                        self.hash_table[state.left.id] = state.left
                    
                        #-------------------------------------------------
                

            # If it does have a left node
            else:
                print('--- else (if state.left)')
                self._add_pull_state_helper(state.left, 
                                    prob, 
                                    flow_name, 
                                    inst=inst, 
                                    path=path+'F',
                                    path_prob= round(state.path_prob * round(1-prob, rdigits), rdigits))


            
            # If it doesn't have a right node
            if not state.right:
                print('--- if not state.right')
                
                right_work_load = state.workload.copy()
                right_work_load[flow_name] = True
                # if it's flow name is true in workload then path_prob * 1
                if state.workload[flow_name]:
                    print('---- state workload was True')
                    right_state = State(status='S',
                                        prob=prob,
                                        workload=right_work_load,
                                        inst=inst ,
                                        path=path+'S',
                                        path_prob=state.path_prob) # main line for pull - for right node (successful attempt)
                else:
                    print('--- if not state.right')
                    right_state = State(status='S',
                                        prob=prob,
                                        workload=right_work_load,
                                        inst=inst ,
                                        path=path+'S',
                                        path_prob=round(state.path_prob*prob, rdigits)) # main line for pull - for right node (successful attempt)
                    
                
                print("--- right_state.id: ", right_state.id)
                if right_state.id in self.hash_table:
                    print('---- right_state.id in self.hash_table')
                    self.hash_table[right_state.id].path_prob += right_state.path_prob
                    state.right = self.hash_table[right_state.id]
                    
                
                else:
                    print('---- else (right_state.id NOT in self.hash_table)')
                    state.right = right_state
                    self.hash_table[state.right.id] = state.right
                    
                        #-------------------------------------------------
            
            # If it does have a right node
            else:
                print('--- else (if state.right)')
                if state:
                    self._add_pull_state_helper(state.right, 
                                        prob, 
                                        flow_name, 
                                        inst=inst, 
                                        path=path+'S', 
                                        path_prob= round(path_prob * prob, rdigits))
                        

    # Adding state after a conditional pull (Assuming the previous pull was not successful)
    def add_conditional_state(self, condition, condition_is_true, condition_is_false, prob=1, inst='', path='', path_prob=1):
        if not self.root:
            return
        
        self._add_conditional_state_helper(self.root, condition, condition_is_true, condition_is_false, prob, inst, path, path_prob)
    
    def _add_conditional_state_helper(self, state, condition, condition_is_true, condition_is_false, prob, inst, path, path_prob):
        rdigits = 3
        if not state.left:  
            if not state.workload.get(condition):  # !has(condition)
                # condition is true
                # instruction, flow_name, channel_number = inst_parser(condition_is_true) # old line
                instruc, flow_name, nodes, channel_number = condition_is_true
                flow_name += nodes
                self._add_pull_state_helper(state, prob, flow_name, inst=condition_is_true, path=path, path_prob= round(path_prob * state.path_prob, rdigits))
            
                
                
            elif state.workload[condition] and condition_is_false:
                #condition is false
                
                # instruction, flow_name, channel_number = inst_parser(condition_is_false) # Old line
                instruc, flow_name, nodes, channel_number = parsed_instruction = condition_is_false
                flow_name += nodes
                self._add_pull_state_helper(state, prob, flow_name, inst=condition_is_false, path=path, path_prob= round(path_prob * state.path_prob, rdigits))
        
        
        else:   # if not, continue looking for leaf nodes
            if state.middle:
                self._add_conditional_state_helper(state.left, condition, condition_is_true, condition_is_false, prob, inst=inst, path=path+'H', path_prob= path_prob)
            
            else:    
                if state.left:
                    self._add_conditional_state_helper(state.left, condition, condition_is_true, condition_is_false, prob, inst=inst, path=path+'F', path_prob= round(path_prob * state.path_prob, rdigits))
                
                if state.right:
                    self._add_conditional_state_helper(state.right, condition, condition_is_true, condition_is_false, prob, inst=inst, path=path+'S', path_prob= round(path_prob * state.path_prob, rdigits))


                
            # state.left = State(status='F', prob=round(1-prob, 3))
            
        
    # Releasing and dropping flows in the tree
    def release_flow(self, flow_name):
        if not self.root:
            self.root = State()
        
        self._release_flow_helper(self.root, flow_name)
    
    def _release_flow_helper(self, state, flow_name):
        if not state.left and not state.right:  # if state is a leaf node
            state.workload[flow_name] = False  
       
        else:                                   # if not, look for leafs
            if state.left:
                self._release_flow_helper(state.left, flow_name)
            
            if state.right:
                self._release_flow_helper(state.right, flow_name)

                
    def drop_flow(self, flow_name):
        if not self.root:
            return False
        
        self._drop_flow_helper(self.root, flow_name)
    
    def _drop_flow_helper(self, state, flow_name):
        if not state.left and not state.right:  # if state is a leaf node
            state.workload.pop(flow_name)
        
        else:                                   # if not, look for leafs
            if state.left:
                self._drop_flow_helper(state.left, flow_name)
            
            if state.right:
                self._drop_flow_helper(state.right, flow_name)


    # Add a state to all leaf nodes after a sleep command
    def add_sleep_state(self, prob=1, flow_name='', inst='', path='', path_prob=1):
        if not self.root:
            self.root = State()
            return
        
        self._add_sleep_state_helper(self.root, prob, flow_name, inst, path, path_prob)
      
    def _add_sleep_state_helper(self, state, prob, flow_name, inst, path, path_prob):
        
        if not state.right and not state.left and not state.middle:
            middle_work_load = state.workload.copy()
            state.middle = State(status='H',
                                prob=prob,
                                workload=middle_work_load,
                                inst=inst ,path=path+'H',
                                path_prob=state.path_prob) # main line for pull - for right node (successful attempt)
            
                    #-------------------------------------------------
        elif state.middle:
            self._add_sleep_state_helper(state.middle, 
                                        prob, 
                                        flow_name, 
                                        inst=inst, 
                                        path=path+'H', 
                                        path_prob= state.path_prob)
                
        else:
            self._add_sleep_state_helper(state.right, 
                                        prob, 
                                        flow_name, 
                                        inst=inst, 
                                        path=path+'S', 
                                        path_prob= state.path_prob)
            
            self._add_sleep_state_helper(state.left, 
                                        prob, 
                                        flow_name, 
                                        inst=inst, 
                                        path=path+'F',
                                        path_prob= state.path_prob)
                
    

    # A function to print the tree in the CLI
    def print_tree(self):
        if not self.root:
            print("Empty tree!")
            return
        
        self._print_tree_helper(self.root, 0)
    
    def _print_tree_helper(self, state, level):
        if not state:
            return
        
        if state.middle:
            self._print_tree_helper(state.middle, level+1)
            # print('\n',"    "*level + str(state.status) +'|'+str(state.path)+f'({state.path_prob})')
        else:
            self._print_tree_helper(state.right, level+1)
            print('\n',"    "*level + str(state.status) +'|'+str(state.path)+f'({state.path_prob})')
            self._print_tree_helper(state.left, level+1)
        
    
    # Printing out a BF Search on the tree to  show all the possible outcome and their probability
    def all_paths(self):
        print("All possible paths using BFS:")
        self.BFS(self.root)   

    def BFS(self, state):
        queue = [[state, [], 1]]
        
        while queue:
            state, path, prob = queue.pop(0)  
            
            if not state.left and not state.right:
                print(' '.join(path + [state.status]), end=' ----->>  ')
                print("Product of probabilities: ", round(prob * state.prob, 3))  # Print the product of probabilities
                
            if state.left:
                queue.append([state.left, path + [state.status], round(prob * state.prob, 3)]) 
                
            if state.right:
                queue.append([state.right, path + [state.status], round(prob * state.prob, 3)])


    # Visualizing the graph with the help of graphviz (Whole tree version)
    def visualize_tree(self):
        if not self.root:
            print("Empty tree!")
            return
        
        graph = Graph('./Output/graph', format='png')
        self._visualize_tree_helper(graph, self.root)
        graph.view()
    
    def _visualize_tree_helper(self, graph, state):
        if not state:
            return
        
        node_id = ''.join([ str(b)[0] for b in list(state.workload.values())])
        
        node_label = str('Path: '+state.path+'\n'+
                         'Workload: '+str(state.workload)+'\n'+
                         'Path Prob: '+str(state.path_prob)+'\n'+
                         'ID: '+ str(len(state.path)) + node_id)
        

        graph.node(state.path, label= node_label)
        
        # print(f'path ({path}) / state.path ({state.path}) += str(state.status ({state.status}))')
        
        # path += str(state.status)
        
        if state.middle:
            # print(f"path ({path}) / state.path ({state.path})+ str(state.right.status) ({state.right.status})")
            print('middle state path prob:', state.path_prob)
            graph.node(state.path, label= node_label)
            
            graph.edge(state.path, state.middle.path, label= state.middle.status+'\n'+str(state.middle.prob)+'--'+str(state.middle.inst))
            
            self._visualize_tree_helper(graph, state.middle)
        
        else:
            if state.left:
                # print(f"path ({path}) / state.path ({state.path}) + str(state.left.status) ({state.left.status})")
                
                graph.node(state.path, label= node_label)
                
                graph.edge(state.path, state.left.path, label="F"+'\n'+str(round(1-state.right.prob, 2))+'--'+str(state.left.inst))
                # graph.edge(state.path, state.left.path, label=state.left.status+'\n'+str(round(1-state.right.prob, 2))+'--'+str(state.left.inst))
                
                self._visualize_tree_helper(graph, state.left)
            
            
            
            if state.right:
                # print(f"path ({path}) / state.path ({state.path})+ str(state.right.status) ({state.right.status})")
                
                graph.node(state.path, label= node_label)
                
                graph.edge(state.path, state.right.path, label= "S"+'\n'+str(state.right.prob)+'--'+str(state.right.inst))
                # graph.edge(state.path, state.right.path, label= state.right.status+'\n'+str(state.right.prob)+'--'+str(state.right.inst))
                
                self._visualize_tree_helper(graph, state.right)


    def search_state(self, state, target_id, age=0):
        
        # print(f'{state.path} == {depth} and {state.workload} == {workload}')
        print(state.id, '==',target_id)
        print('search_state')
        
        if state.id == target_id:
            return state
        
        else:
            if state.middle:
                print('if state.middle:')
                result = self.search_state(state.middle, target_id, age=age+1)
                if result:
                    return result
            
            else:
                if state.left:
                    print('if state.left:')
                    result = self.search_state(state.left, target_id, age=age+1)
                    if result:
                        return result
                    
                if state.right:
                    print('if state.right')
                    result = self.search_state(state.right, target_id, age=age+1)
                    if result:
                        return result
                
