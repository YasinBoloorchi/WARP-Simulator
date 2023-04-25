from graphviz import Graph
from time import sleep
import re

class State:
    def __init__(self, data='S', left=None, right=None, prob=1, workload={}, inst=''):
        self.data = data
        self.left = left
        self.right = right
        self.prob = prob
        self.inst = inst
        self.workload = workload

class StatesTree:
    def __init__(self, root=None):
        self.root = root
    
    # Adding state after a pull 
    def add_state(self, prob=1, flow_name='', inst=''):
        if not self.root:
            self.root = State()
            return
        
        self._add_state_helper(self.root, prob, flow_name, inst)
        
    def _add_state_helper(self, state, prob, flow_name, inst):
        if not state.left:
            state.left = State(data='F', prob=round(1-prob, 2), workload=state.workload.copy(), inst=inst)  #main line for pull - for left node (failed attempt)
        else:
            self._add_state_helper(state.left, prob, flow_name, inst=inst)
        
        if not state.right:
            right_workload = state.workload.copy()
            right_workload[flow_name] = True
            state.right = State(data='S', prob=prob, workload=right_workload) # main line for pull - for right node (successful attempt)
        else:
            self._add_state_helper(state.right, prob, flow_name, inst=inst)
            
    # Adding state after a conditional pull (Assuming the previous pull was not successful)
    def add_conditional_state(self, condition, condition_is_true, condition_is_false, prob=1, inst=''):
        if not self.root:
            return
        
        self._add_conditional_state_helper(self.root, condition, condition_is_true, condition_is_false, prob, inst)
    
    def _add_conditional_state_helper(self, state, condition, condition_is_true, condition_is_false, prob, inst):
        if not state.left:  
            if not state.workload.get(condition):  # !has(condition)
                # condition is true
                print(f'If condition !has({condition}) is true')
                
                instruction, flow_name, channel_number = inst_parser(condition_is_true)
                
                self._add_state_helper(state, prob, flow_name, inst=condition_is_true)
                
                
                
            elif state.workload[condition] and condition_is_false:
                #condition is false
                print(f'If condition !has({condition}) is false')
                print(inst_parser(condition_is_false))
                instruction, flow_name, channel_number = inst_parser(condition_is_false)
                
                self._add_state_helper(state, prob, flow_name, inst=condition_is_false)
        
        
        else:   # if not, continue looking for leaf nodes
            if state.left:
                self._add_conditional_state_helper(state.left, condition, condition_is_true, condition_is_false, prob, inst=inst)
            
            if state.right:
                self._add_conditional_state_helper(state.right, condition, condition_is_true, condition_is_false, prob, inst=inst)


                
            # state.left = State(data='F', prob=round(1-prob, 2))
              
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

    # A function to print the tree in the CLI
    def print_tree(self):
        if not self.root:
            print("Empty tree!")
            return
        
        self._print_tree_helper(self.root, 0)
    
    def _print_tree_helper(self, state, level):
        if not state:
            return
        
        self._print_tree_helper(state.right, level+1)
        print("    "*level + str(state.data) + str(state.workload))
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


    # Visualizing the graph with the help of graphviz
    
    # vvvvvvvvvvvvvvvvvvvvvvvvvvv UNDER CONSTRUCTION vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    def visualize_tree(self):
        if not self.root:
            print("Empty tree!")
            return
        
        g = Graph('G', format='png')
        self._visualize_tree_helper(g, self.root, path='')
        g.view()
    
    def _visualize_tree_helper(self, g, state, path):
        if not state:
            return
        
        node_id = ''.join([ str(b)[0] for b in list(state.workload.values())])
        print('='*35, '\n', f'node_id: ({node_id}), path ({path}) += str(state.data ({state.data}))', '\n','='*35)
        
        # g.node(str(state.workload), label='Path: '+path+'\n'+str(state.workload))
        
        # g.view()
        # path += str(state.data)
        
        if state.left:
            left_node_id = ''.join([ str(b)[0] for b in list(state.left.workload.values())])
            print('='*35,'\n',f"left_node_id: ({left_node_id}), path ({path}) + str(state.left.data) ({state.left.data})", '\n', '='*35)
            
            g.node(left_node_id, label= 'Path: '+path+str(state.left.data)+'\n'+str(state.left.workload))
            g.edge(node_id, left_node_id, label= state.left.data+'\n'+'['+str(round(1-state.right.prob, 2))+'--'+str(state.left.inst)+']')

            # g.view()
            self._visualize_tree_helper(g, state.left, path+str(state.left.data))
        
        if state.right:
            right_node_id = ''.join([ str(b)[0] for b in list(state.right.workload.values())])
            print('='*35,'\n',f"right_node_id: ({right_node_id}), path ({path}) + str(state.right.data) ({state.right.data})", '\n','='*35)
            
            g.node(right_node_id, label= 'Path: '+path+str(state.right.data)+'\n'+str(state.right.workload))
            g.edge(node_id, right_node_id, label= state.right.data+'\n'+'['+str(state.right.prob)+'--'+str(state.left.inst)+']')

            # g.view()
            self._visualize_tree_helper(g, state.right, path+str(state.right.data))
        

        # g.view()
    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

# ================================================================


# Parsing the Warp instruction from a file
def parse_instructions(instruction_file_path):
    with open(instruction_file_path, 'r') as instructions_file:

        instructions = [[inst.split(' ', maxsplit=1)[0], inst.strip()] for inst in instructions_file.readlines() if inst.strip()]
        print(instructions)
        # instructions = [[inst[0], inst[1].replace(')', '').replace('(', '').split(',')] for inst in instructions]
        
        instructions_file.close()

        
    return instructions

# Parser function for different types of instructions
def inst_parser(instruction):
    parsed_inst = re.findall('^(\w*)\s*\((\w\d),*(\W*\d*\w*)\)$', instruction)[0]
    
    return parsed_inst


def if_inst_parser(instruction):
    parsd_if_inst = re.findall('^\w*\s*\W\w*\((\w\d)\)\s*\w*\s*(\w*\s*\(\s*\w+\d+\s*,\s*\W\d+\))\s*\w*\s*(\w*\s*\(\s*\w+\d+\s*,\s*\W\d+\))*$', instruction)[0]
    
    return parsd_if_inst


# Running the instructions that been parsed from the file
def run_instruction(instruction_file_path):
    # initial variables
    instructions = parse_instructions(instruction_file_path)
    
    # Generate States tree and initial state
    tree = StatesTree()
    tree.add_state()

    # warp code execution loop
    for inst in instructions:
        inst_type = inst[0]
        instruction = inst[1]
        
        # print('instruction type: ', inst_type, '-- instruction: ', instruction)
        
        if inst_type == 'release':
            # Parse release command => ('release', 'F1', 'AC')
            parsed_instruction = inst_parser(instruction)
        
            flow_name = parsed_instruction[1]
            address = parsed_instruction[2]
            
            # workload[flow_name] = {'source': address[0], 'dest':address[1], 'has':False}
            
            tree.release_flow(flow_name)
            
        
        elif inst_type == 'drop':
            # Parse drop command
            parsed_instruction = inst_parser(instruction)
            
            flow_name = parsed_instruction[1]
            
            tree.drop_flow(flow_name)


        elif inst_type == 'pull':
            # Parse pull command = >('pull', 'F0', '#0')

            instruc, flow_name, channel_number = inst_parser(instruction)
            print(inst, flow_name, channel_number)
            
            tree.add_state(prob=0.8, flow_name=flow_name, inst=instruction)
            
            
        elif inst_type == 'if':
            # Parse if command => ('F0', 'pull(F0,#1)', 'pull(F0,#1)')
            condition, condition_is_true, condition_is_false = if_inst_parser(instruction)            
            
            print(condition, condition_is_true, condition_is_false)
            
            tree.add_conditional_state(condition, condition_is_true, condition_is_false, prob=0.8)

    tree.print_tree()
        
        
    # tree.all_paths()

    tree.visualize_tree()

# A dummy function for running a set of instructions
def test_instructions():
    
    # Create the tree and initial state
    tree = StatesTree()
    tree.add_state()
    
    tree.add_state(0.8)
    tree.add_conditional_state(0.9)
    
    tree.add_state(0.8)

    tree.visualize_tree()
    sleep(0.1) 
    tree.all_paths()
    tree.print_tree()

# A dummy function to test parsers
def test_parsers():
    # instruction = 'pull (F0,#0)'
    # instruction = 'release (F1,AC)'
    # instruction = 'drop (F0)'
    
    # inst, flow_name, channel_number = inst_parser(instruction)
    # print(inst, flow_name, channel_number)


    instruction = 'if !has(F0) then pull(F0,#1) else pull(F1,#1)'
    condition, condition_is_true, condition_is_false = if_inst_parser(instruction)            
    print(condition, condition_is_true, condition_is_false)

    
def main():
    run_instruction('./Instructions.wrp')
    # test_instructions()
    # test_parsers()


if __name__ == "__main__":
    # parse_instructions('./Instructions.wrp')
    main()
