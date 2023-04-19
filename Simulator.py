from graphviz import Graph
from time import sleep

class State:
    def __init__(self, data='S', left=None, right=None, prob=1):
        self.data = data
        self.left = left
        self.right = right
        self.prob = prob

class StatesTree:
    def __init__(self, root=None):
        self.root = root
    
    # Adding state after a pull 
    def add_state(self, prob=1):
        if not self.root:
            self.root = State()
            return
        
        self._add_state_helper(self.root, prob)
        
    
    def _add_state_helper(self, state, prob):
        if not state.left:
            state.left = State(data='F', prob=round(1-prob, 2))
        else:
            self._add_state_helper(state.left, prob)
        
        if not state.right:
            state.right = State(data='S', prob=prob)
        else:
            self._add_state_helper(state.right, prob)
            
    
    # Adding state after a conditional pull (Assuming the previous pull was not successful)
    def add_conditional_state(self, prob=1):
        if not self.root:
            self.root = State()
            return
        
        self._add_conditional_state_helper(self.root, prob)
    
    def _add_conditional_state_helper(self, state, prob):
        if not state.left:
            state.left = State(data='F', prob=round(1-prob, 2))
        else:
            self._add_state_helper(state.left, prob)
        
    
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
        print("    "*level + str(state.data))
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
    def visualize_tree(self):
        if not self.root:
            print("Empty tree!")
            return
        
        g = Graph('G', format='png')
        self._visualize_tree_helper(g, self.root)
        g.view()
    
    def _visualize_tree_helper(self, g, state):
        if not state:
            return
        
        g.node(str(id(state)), label=str(state.data))  
        
        if state.left:
            g.node(str(id(state.left)), label=str(state.left.data))
            g.edge(str(id(state)), str(id(state.left)), label=str(round(1-state.right.prob, 2)))
            self._visualize_tree_helper(g, state.left)
        
        if state.right:
            g.node(str(id(state.right)), label=str(state.right.data))
            g.edge(str(id(state)), str(id(state.right)), label=str(state.right.prob))
            self._visualize_tree_helper(g, state.right)



# Parsing the Warp instruction from a file
def parse_instructions(instruction_file_path):
    with open(instruction_file_path, 'r') as instructions_file:

        instructions = [[inst.split(' ', maxsplit=1)[0], inst.strip()] for inst in instructions_file.readlines() if inst.strip()]
        print(instructions)
        # instructions = [[inst[0], inst[1].replace(')', '').replace('(', '').split(',')] for inst in instructions]
        
        instructions_file.close()

    for ins in instructions:
        print(ins)
        
    # return instructions

# Running the instructions that been parsed from the file
def run_instruction(instruction_file_path):
    
    # initial variables
    instructions = parse_instruction(instruction_file_path)
    workload = {}
    
    # Generate States tree and initial state
    tree = StatesTree()
    tree.add_state()

    # warp code execution loop
    for inst in instructions:
        command = inst[0]
        parameters = inst[1]
        
        print('command: ', command, '-- parameters: ', parameters)
        
        if command == 'pull':
            tree.add_state()
            
            
        elif command == 'if':
            tree.add_conditional_state()
            
            
        elif command == 'release':
            flow_name = parameters[0]
            address = parameters[1]
            
            workload[flow_name] = {'source':address[0], 'target':address[1]}
            
        elif command == 'drop':
            flow_name = parameters[0]
            print('dropping flow',flow_name ,workload[flow_name])
            workload.pop(flow_name)
            
            
        print('Workload: ', workload)
        # tree.print_tree()
    tree.all_paths()

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
    
    
def main():
    # run_instruction('./Instructions.wrp')
    test_instructions()

if __name__ == "__main__":
    parse_instructions('./Instructions.wrp')
    # main()
