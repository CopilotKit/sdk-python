"""Step 2. Restart from serialized state
"""
import sys
import pickle
from .graph import graph
from .copilotkit import step_continue


# Get the name from the command line arguments
if len(sys.argv) < 2:
    print("Error: Missing name argument")
    sys.exit(1)
name = sys.argv[1]

with open('./state.pickle', 'rb') as f:
    serialized_state = pickle.load(f)

step_continue(graph, serialized_state, name)
