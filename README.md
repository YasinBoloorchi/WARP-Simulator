# Simulator README

This repository contains a simulator that reads instructions from the file `Instructions.wrp` and generates a picture of a graph representing all possible states of the code.

## Getting Started

To use the simulator, follow the instructions below:

### Prerequisites

Make sure you have the following software installed:

- Python 3
- Graphviz

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/simulator.git
   ```

2. Change into the project directory:

   ```bash
   cd simulator
   ```

3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. Place your instructions in the `Instructions.wrp` file.

2. Run the simulator:

   ```bash
   python simulator.py
   ```

3. The simulator will generate a picture of the graph representing all possible states of the code and save it as `graph.png`.

## Code Overview

The `simulator.py` file contains the implementation of the simulator. It defines several classes and functions to handle the simulation logic.

- `Node` class represents a node in the graph.
- `State` class represents a state in the simulation.
- `StatesTree` class represents the tree structure for the states.
- `add_state` method adds a state to the tree after a pull.
- `add_conditional_state` method adds a state after a conditional pull.
- `release_flow` method releases and drops flows in the tree.
- `drop_flow` method drops a flow from the tree.
- `add_sleep_state` method adds a state to all leaf nodes after a sleep command.
- `print_tree` method prints the tree in the command-line interface.
- `all_paths` method prints all possible paths using breadth-first search.
- `visualize_tree` method generates a graph of the tree using Graphviz.
- `visualize_DAG` method generates a directed acyclic graph (DAG) of the tree using Graphviz.

## Contributing

Contributions to this project are welcome. If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.