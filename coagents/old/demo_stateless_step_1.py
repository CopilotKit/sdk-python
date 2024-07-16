"""Step 1. Serialize the state
"""
import pickle
from .graph import graph
from .copilotkit import step_initial, serialize_checkpointer

event = step_initial(graph)

# Save state to ./state.pickle
with open('./state.pickle', 'wb') as f:
    state = serialize_checkpointer(graph)
    pickle.dump(state, f)

if event["copilot"]["ask_user"]:
    print(event["copilot"]["ask_user"]["question"])
