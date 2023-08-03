from typing import Any, Union, get_origin

try:
    from types import UnionType  # type: ignore[attr-defined]
except ImportError:
    UnionType = None


def is_union(tp: Any) -> bool:
    origin = get_origin(tp)
    return origin == Union or (UnionType is not None and origin == UnionType)


NoneType = type(None)


def normalize_type(tp: Any) -> Any:
    if tp == NoneType or tp is None:
        return None
    return tp
