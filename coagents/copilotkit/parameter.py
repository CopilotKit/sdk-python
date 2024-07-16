"""Parameter classes for CopilotKit"""

from typing import TypedDict, Optional, Literal, List

class BaseParameter(TypedDict):
    """Base parameter class"""
    name: str
    description: Optional[str]
    required: Optional[bool]

class StringParameter(BaseParameter):
    """String parameter class"""
    type: Literal["string"]
    enum: Optional[list[str]]

class NumberParameter(BaseParameter):
    """Number parameter class"""
    type: Literal["number"]

class BooleanParameter(BaseParameter):
    """Boolean parameter class"""
    type: Literal["boolean"]

class ObjectParameter(BaseParameter):
    """Object parameter class"""
    type: Literal["object"]
    attributes: List[BaseParameter]

class ObjectArrayParameter(BaseParameter):
    """Object array parameter class"""
    type: Literal["object[]"]
    attributes: List[BaseParameter]

class StringArrayParameter(BaseParameter):
    """String array parameter class"""
    type: Literal["string[]"]

class NumberArrayParameter(BaseParameter):
    """Number array parameter class"""
    type: Literal["number[]"]

class BooleanArrayParameter(BaseParameter):
    """Boolean array parameter class"""
    type: Literal["boolean[]"]
