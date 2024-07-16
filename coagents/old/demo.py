"""CopilotKit SDK demo
"""

from .copilotkit import  CopilotKitSDK
from .graph import graph

CopilotKitSDK(agents=[graph]).run()
