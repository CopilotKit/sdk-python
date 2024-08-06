"""Parameter classes for CopilotKit"""

from typing import TypedDict, Optional, Literal, List

class BaseParameter(TypedDict):
    """Base parameter class"""
    name: str
    description: Optional[str]
    required: Optional[bool]


def normalize_parameters(parameters: Optional[List[BaseParameter]]) -> List[BaseParameter]:
    """Normalize the parameters to ensure they have the correct type and format."""
    if parameters is None:
        return []
    return [_normalize_parameter(parameter) for parameter in parameters]

def _normalize_parameter(parameter: BaseParameter) -> BaseParameter:
    """Normalize a parameter to ensure it has the correct type and format."""
    if not hasattr(parameter, 'type'):
        parameter['type'] = 'string'
    if not hasattr(parameter, 'required'):
        parameter['required'] = False
    if not hasattr(parameter, 'description'):
        parameter['description'] = ''
    
    if parameter['type'] == 'object' or parameter['type'] == 'object[]':
        parameter['attributes'] = normalize_parameters(parameter.get('attributes'))
    return parameter

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
