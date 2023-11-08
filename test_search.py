from collections import defaultdict

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = defaultdict(list)

    def addEdge(self, u, v):
        self.graph[u].append(v)

    def findPaths(self, s, d):
        stack = [(s, [s])]  # Initialize the stack with the starting node and its path
        visited = [False] * self.V
        all_paths = []

        while stack:
            current, path = stack.pop()
            visited[current] = True

            if current == d:
                all_paths.append(path)
            else:
                for neighbor in self.graph[current]:
                    if not visited[neighbor]:
                        new_path = path + [neighbor]
                        stack.append((neighbor, new_path))
    
        return all_paths

g = Graph(4)
g.addEdge(0, 1)
g.addEdge(0, 2)
g.addEdge(0, 3)
g.addEdge(2, 0)
g.addEdge(2, 1)
g.addEdge(1, 3)

s = 2
d = 3
print("Following are all different paths from %d to %d:" % (s, d))
all_paths = g.findPaths(s, d)
for path in all_paths:
    print(path)
