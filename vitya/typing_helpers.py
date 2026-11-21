import types
from typing import Any, Union, get_origin

UnionType = getattr(types, 'UnionType', None)


def is_union(tp: Any) -> bool:
    origin = get_origin(tp)
    return origin is Union or (UnionType is not None and origin is UnionType)


NoneType = type(None)


def normalize_type(tp: Any) -> Any:
    if tp == NoneType or tp is None:
        return None
    return tp
