"""Parameter classes for CopilotKit"""

from typing import TypedDict, Optional, Literal, List, Union

class Parameter(TypedDict):
    """Base parameter class"""
    name: str
    description: Optional[str]
    required: Optional[bool]
    type: Optional[
        Union[
            str,
            Literal[
                "string", 
                "number", 
                "boolean", 
                "object", 
                "object[]", 
                "string[]", 
                "number[]", 
                "boolean[]"
            ]
        ]
    ]
    attributes: Optional[List['Parameter']]

def normalize_parameters(parameters: Optional[List[Parameter]]) -> List[Parameter]:
    """Normalize the parameters to ensure they have the correct type and format."""
    if parameters is None:
        return []
    return [_normalize_parameter(parameter) for parameter in parameters]

def _normalize_parameter(parameter: Parameter) -> Parameter:
    """Normalize a parameter to ensure it has the correct type and format."""
    if not hasattr(parameter, 'type'):
        parameter['type'] = 'string'
    if not hasattr(parameter, 'required'):
        parameter['required'] = True
    if not hasattr(parameter, 'description'):
        parameter['description'] = ''

    if parameter['type'] == 'object' or parameter['type'] == 'object[]':
        parameter['attributes'] = normalize_parameters(parameter.get('attributes'))
    return parameter
