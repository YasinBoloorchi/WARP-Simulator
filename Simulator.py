from graphviz import Graph
from time import sleep
import re

class Node:
    def __init__(self, node_id, label=None):
        self.node_id = node_id
        self.label = label
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

class State:
    def __init__(self, data='S', left=None, right=None, middle=None, prob=1, workload={}, inst='', path = '', path_prob=1):
        self.data = data
        self.left = left
        self.right = right
        self.middle = middle
        self.prob = prob
        self.inst = inst
        self.workload = workload
        self.path = path
        self.path_prob = path_prob

class StatesTree:
    def __init__(self, root=None):
        self.root = root
    
    # Adding two states to all leaf after a pull 
    def add_state(self, prob=1, flow_name='', inst='', path='', path_prob=1):
        if not self.root:
            self.root = State()
            return
        
        self._add_state_helper(self.root, prob, flow_name, inst, path, path_prob)
      
    def _add_state_helper(self, state, prob, flow_name, inst, path, path_prob):
        rdigits = 3
        
        if state.middle:
                self._add_state_helper(state.middle, 
                prob, 
                flow_name, 
                inst=inst, 
                path=path+'H', 
                path_prob= path_prob)
        
        else:
            if not state.left:
                right_work_load = state.workload.copy()
                right_work_load[flow_name] = False
                state.left = State(data='F', 
                                prob=round(1-prob, rdigits), 
                                workload=state.workload.copy(), 
                                inst=inst, 
                                path=path+'F', 
                                path_prob=round(path_prob*round(1-prob, rdigits), rdigits))  #main line for pull - for left node (failed attempt)
                        #-------------------------------------------------

            else:
                self._add_state_helper(state.left, 
                                    prob, 
                                    flow_name, 
                                    inst=inst, 
                                    path=path+'F',
                                    path_prob= round(path_prob * round(1-prob, rdigits), rdigits))
            
            
            if not state.right:
                right_work_load = state.workload.copy()
                right_work_load[flow_name] = True
                state.right = State(data='S',
                                    prob=prob,
                                    workload=right_work_load,
                                    inst=inst ,path=path+'S',
                                    path_prob=round(path_prob*prob, rdigits)) # main line for pull - for right node (successful attempt)

                        #-------------------------------------------------
            else:
                self._add_state_helper(state.right, 
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
                self._add_state_helper(state, prob, flow_name, inst=condition_is_true, path=path, path_prob= round(path_prob * state.path_prob, rdigits))
            
                
                
            elif state.workload[condition] and condition_is_false:
                #condition is false
                
                # instruction, flow_name, channel_number = inst_parser(condition_is_false) # Old line
                instruc, flow_name, nodes, channel_number = parsed_instruction = condition_is_false
                flow_name += nodes
                self._add_state_helper(state, prob, flow_name, inst=condition_is_false, path=path, path_prob= round(path_prob * state.path_prob, rdigits))
        
        
        else:   # if not, continue looking for leaf nodes
            if state.middle:
                self._add_conditional_state_helper(state.left, condition, condition_is_true, condition_is_false, prob, inst=inst, path=path+'H', path_prob= path_prob)
            
            else:    
                if state.left:
                    self._add_conditional_state_helper(state.left, condition, condition_is_true, condition_is_false, prob, inst=inst, path=path+'F', path_prob= round(path_prob * state.path_prob, rdigits))
                
                if state.right:
                    self._add_conditional_state_helper(state.right, condition, condition_is_true, condition_is_false, prob, inst=inst, path=path+'S', path_prob= round(path_prob * state.path_prob, rdigits))


                
            # state.left = State(data='F', prob=round(1-prob, 3))
            
        
    # Releasing and dropping flows in the tree
    def release_flow(self, flow_name):
        if not self.root:
            return
        
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
            state.middle = State(data='H',
                                prob=prob,
                                workload=middle_work_load,
                                inst=inst ,path=path+'H',
                                path_prob=path_prob) # main line for pull - for right node (successful attempt)
            
                    #-------------------------------------------------
        elif state.middle:
            self._add_sleep_state_helper(state.middle, 
                                        prob, 
                                        flow_name, 
                                        inst=inst, 
                                        path=path+'H', 
                                        path_prob= path_prob)
                
        else:
            self._add_sleep_state_helper(state.right, 
                                        prob, 
                                        flow_name, 
                                        inst=inst, 
                                        path=path+'S', 
                                        path_prob= path_prob)
            
            self._add_sleep_state_helper(state.left, 
                                        prob, 
                                        flow_name, 
                                        inst=inst, 
                                        path=path+'F',
                                        path_prob= path_prob)
                
    

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
            # print('\n',"    "*level + str(state.data) +'|'+str(state.path)+f'({state.path_prob})')
        else:
            self._print_tree_helper(state.right, level+1)
            print('\n',"    "*level + str(state.data) +'|'+str(state.path)+f'({state.path_prob})')
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
                print(' '.join(path + [state.data]), end=' ----->>  ')
                print("Product of probabilities: ", round(prob * state.prob, 3))  # Print the product of probabilities
                
            if state.left:
                queue.append([state.left, path + [state.data], round(prob * state.prob, 3)]) 
                
            if state.right:
                queue.append([state.right, path + [state.data], round(prob * state.prob, 3)])


    # Visualizing the graph with the help of graphviz (Whole tree version)
    def visualize_tree(self):
        if not self.root:
            print("Empty tree!")
            return
        
        graph = Graph('graph', format='png')
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
        
        # print(f'path ({path}) / state.path ({state.path}) += str(state.data ({state.data}))')
        
        # path += str(state.data)
        
        if state.middle:
            # print(f"path ({path}) / state.path ({state.path})+ str(state.right.data) ({state.right.data})")
            
            graph.node(state.path, label= node_label)
            
            graph.edge(state.path, state.middle.path, label= state.middle.data+'\n'+str(state.middle.prob)+'--'+str(state.middle.inst))
            
            self._visualize_tree_helper(graph, state.middle)
        
        else:
            if state.left:
                # print(f"path ({path}) / state.path ({state.path}) + str(state.left.data) ({state.left.data})")
                
                graph.node(state.path, label= node_label)
                
                graph.edge(state.path, state.left.path, label=state.left.data+'\n'+str(round(1-state.right.prob, 2))+'--'+str(state.left.inst))
                
                self._visualize_tree_helper(graph, state.left)
            
            if state.right:
                # print(f"path ({path}) / state.path ({state.path})+ str(state.right.data) ({state.right.data})")
                
                graph.node(state.path, label= node_label)
                
                graph.edge(state.path, state.right.path, label= state.right.data+'\n'+str(state.right.prob)+'--'+str(state.right.inst))
                
                self._visualize_tree_helper(graph, state.right)
            

        
    def visualize_DAG(self):
        if not self.root:
            print("Empty tree!")
            return
        
        DAG = Graph('DAG', format='png')
        self._visualize_DAG_helper(DAG, self.root, path='')
        DAG.view()
    
    def _visualize_DAG_helper(self, DAG, state, path):
        if not state:
            return
        
        node_id = ''.join([ str(b)[0] for b in list(state.workload.values())])
        node_depth = str(len(state.path))
        node_id = node_depth + node_id
        
        node_label = str('Path: '+state.path+'\n'+
                         'Workload: '+str(state.workload)+'\n'+
                         'ID: '+ node_id)
        
        
        print('='*35, '\n', f'node_id: ({node_id}), path ({path}) += str(state.data ({state.data}))', '\n','='*35)
        
        DAG.node(node_id, label= node_label)
        
        # DAG.view()
        # path += str(state.data)
        
        if state.middle:
            middle_node_id = ''.join([ str(b)[0] for b in list(state.middle.workload.values())])
            node_depth = str(len(state.middle.path))
            middle_node_id = node_depth + middle_node_id
            
            # print('='*35,'\n',f"middle_node_id: ({middle_node_id}), path ({path}) + str(state.middle.data) ({state.middle.data})", '\n', '='*35)
            
            DAG.node(node_id, 
                    label= node_label)
            
            
            DAG.edge(node_id, middle_node_id, 
                    label= state.middle.data+
                    '\n'+'['+str(state.middle.prob)+'--'+str(state.middle.inst)+']')

            # DAG.view()
            self._visualize_DAG_helper(DAG, state.middle, path+str(state.middle.data))
        
        else:
        
            if state.left:
                left_node_id = ''.join([ str(b)[0] for b in list(state.left.workload.values())])
                node_depth = str(len(state.left.path))
                left_node_id = node_depth + left_node_id
                
                # print('='*35,'\n',f"left_node_id: ({left_node_id}), path ({path}) + str(state.left.data) ({state.left.data})", '\n', '='*35)
                
                DAG.node(node_id, 
                        label= node_label+left_node_id)
                
                
                DAG.edge(node_id, left_node_id, 
                        label= state.left.data+
                        '\n'+'['+str(round(1-state.right.prob, 2))+'--'+str(state.left.inst)+']')

                # DAG.view()
                self._visualize_DAG_helper(DAG, state.left, path+str(state.left.data))
            
            
            if state.right:
                right_node_id = ''.join([ str(b)[0] for b in list(state.right.workload.values())])
                node_depth = str(len(state.right.path))
                right_node_id = node_depth + right_node_id
                
                # print('='*35,'\n',f"right_node_id: ({right_node_id}), path ({path}) + str(state.right.data) ({state.right.data})", '\n','='*35)
                
                DAG.node(node_id, 
                        label= node_label)
                
                
                DAG.edge(node_id, right_node_id,
                        label= state.right.data+
                        '\n'+'['+str(state.right.prob)+'--'+str(state.left.inst)+']')

                # DAG.view()
                self._visualize_DAG_helper(DAG, state.right, path+str(state.right.data))
            

        # DAG.view()
        

# ================================================================

# Parsing the Warp instruction from a file
def parse_instructions(instruction_file_path):
    with open(instruction_file_path, 'r') as instructions_file:
        instructions = [inst.strip() for inst in instructions_file.readlines()]
        
        # instructions = [[inst.split(' ', maxsplit=1)[0], inst.strip()] for inst in instructions_file.readlines() if inst.strip()]
        # print(instructions)
        
        slot_num = 0
        slots = [[]]
        
        for inst in instructions:
            if '--' in inst:
                slot_num += 1
                slots.append([])
            else:
                instruction = (inst.split(' ', maxsplit=1)[0], inst.strip())
                slots[slot_num].append(instruction)
                
        instructions = slots.copy()
        instructions_file.close()
        
    return instructions

# Parser function for different types of instructions
def inst_parser(instruction):
    parsed_inst = re.findall('(\w*)\s*\(\s*(\w\d+)\s*,*\s*(\w+)*\s*,*(\#\d+)*\s*\)', instruction)
    
    print('\n\n','Parsed ====>',parsed_inst,'\n\n')
    return parsed_inst


def if_inst_parser(instruction):
    parsd_if_inst = re.findall('^\w*\s*\W\w*\((\w\d),\w{2}\)\s*\w*\s*(\w*\s*\(\s*\w+\d+\s*,\s*\W\d+,\w{2}\))\s*\w*\s*(\w*\s*\(\s*\w+\d+\s*,\s*\W\d+,\w{2}\))*$', instruction)[0]
    
    return parsd_if_inst


# Running the instructions that been parsed from the file
def run_loop(instruction_file_path):
    # initial variables
    instructions = parse_instructions(instruction_file_path)
    
    # Generate States tree and initial state
    tree = StatesTree()
    tree.add_state()

    
    # [['release', 'release (F0,BC)'], ['release', 'release (F1,AC)'], ['pull', 'pull (F0, #0)'], ['if', 'if !has(F0) then pull(F0,#1) else pull (F1,#1)'], ['pull', 'pull (F1, #2)']]
    # warp code execution loop
    for slot in instructions:
        pull_count = 0
        
        for inst in slot:
            
            inst_type = inst[0]
            instruction = inst[1]
            print(inst, '| inst type: ', inst_type, '| instruction: ', instruction)
            
            if inst_type == 'release':
                parsed_instruction = inst_parser(instruction)[0]
                # inst_parser => [('release', 'F0', 'BA', '')]
            
                flow_name = parsed_instruction[1]+parsed_instruction[2]
                
                # workload[flow_name] = {'source': address[0], 'dest':address[1], 'has':False}
                
                tree.release_flow(flow_name)
                
            
            elif inst_type == 'drop':
                parsed_instruction = inst_parser(instruction)[0]
                # inst_parser => [('drop', 'F0', 'BA', '')] 
                
                flow_name = parsed_instruction[1]+parsed_instruction[2]
                
                tree.drop_flow(flow_name)


            elif inst_type == 'pull' or inst_type == 'push':
                pull_count += 1
                parsed_instruction = inst_parser(instruction)
                # inst_parser => [('pull', 'F0', 'BA', '#0')] 
                
                instruc, flow_name, nodes, channel_number = parsed_instruction = inst_parser(instruction)[0]
                flow_name+=nodes
                tree.add_state(prob=0.8, flow_name=flow_name, inst=instruction)
                
                
            elif inst_type == 'if':
                pull_count += 1
                parsed_instruction = inst_parser(instruction)
                # inst_parser => [('has', 'F0', 'BA', ''), ('pull', 'F0', 'BA', '#1'), ('pull', 'F0', 'AC', '#1')] 
                
                condition, condition_is_true, condition_is_false = inst_parser(instruction)         

                #          F0         pull(F0,#1)         pull (F1,#1)
                #         vvvv         vvvvvvvv              vvvv
                # print(condition, condition_is_true, condition_is_false)
                
                flow_name = condition[1]
                nodes = condition[2]
                flow_name += nodes
                condition = flow_name
                
                tree.add_conditional_state(condition, condition_is_true, condition_is_false, prob=0.8)

    
            elif inst_type == 'sleep':
                print(instruction)
                tree.add_sleep_state(inst='sleep')

        if pull_count > 1:
            raise Exception('Unexceptable number of pull/push requests in a single slot.')
        
    tree.visualize_tree()

    # tree.print_tree()
    
    # tree.all_paths()

    tree.visualize_DAG()

    
def main():
    run_loop('./HW5-1.wrp')
    # parse_instructions('./NEW_Instructions.wrp')

if __name__ == "__main__":
    # parse_instructions('./Instructions.wrp')
    main()
