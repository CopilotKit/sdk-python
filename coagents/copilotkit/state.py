"""State for CopilotKit"""

from typing import TypedDict, Optional

class CopilotAskState(TypedDict):
    """State for asking the user"""
    question: str
    answer: Optional[str]

class CopilotMessageState(TypedDict):
    """State for sending a message"""
    text: str

class CoagentState(TypedDict):
    """State for CopilotKit"""
    ask: Optional[CopilotAskState]
    message: Optional[CopilotMessageState]
