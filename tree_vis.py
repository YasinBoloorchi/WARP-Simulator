from graphviz import Graph

class State:
    def __init__(self, data='S', left=None, right=None):
        self.data = data
        self.left = left
        self.right = right

class StatesTree:
    def __init__(self, root=None):
        self.root = root
    
    def add_state(self):
        if not self.root:
            self.root = State()
            return
        
        self._add_state_helper(self.root)
    
    def _add_state_helper(self, state):
        if not state.left:
            state.left = State(data='F')
        else:
            self._add_state_helper(state.left)
        
        if not state.right:
            state.right = State(data='S')
        else:
            self._add_state_helper(state.right)
    
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
        
    def all_paths(self):
        print("All possible paths using BFS:")
        self.BFS(self.root)
        
    def BFS(self, state):
        queue = [[state, []]]
        
        while queue:
            state, path = queue.pop(0)
            
            if not state.left and not state.right:
                print(' '.join(path + [state.data]))
                
            if state.left:
                queue.append([state.left, path + [state.data]])
                
            if state.right:
                queue.append([state.right, path + [state.data]])
    
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

        g.node(str(state.data))
        if state.left:
            g.edge(str(state.data), str(state.left.data), label='0')
            self._visualize_tree_helper(g, state.left)
        if state.right:
            g.edge(str(state.data), str(state.right.data), label='1')
            self._visualize_tree_helper(g, state.right)


tree = StatesTree()
tree.add_state()
tree.add_state()
tree.add_state()
tree.add_state()
tree.visualize_tree()