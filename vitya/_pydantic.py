"""Version-specific Pydantic error classes used by the domain validators."""
from pydantic.version import VERSION

PYDANTIC_V2 = VERSION.split('.')[0] == '2'

if PYDANTIC_V2:
    PydanticTypeError = TypeError
    PydanticValueError = ValueError
else:
    from pydantic.errors import PydanticTypeError, PydanticValueError

__all__ = ['PYDANTIC_V2', 'PydanticTypeError', 'PydanticValueError']
