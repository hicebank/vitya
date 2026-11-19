"""Core-schema helpers for Pydantic 2."""
from decimal import Decimal
from typing import Any, Callable, Iterator, Type, get_args

from ._pydantic import PYDANTIC_V2
from .typing_helpers import is_union

if PYDANTIC_V2:
    from pydantic_core import ValidationError, core_schema

    def nullable_occurrences(annotation: Any, target: Type[Any], nullable: bool = False) -> Iterator[bool]:
        if annotation is target:
            yield nullable
            return
        args = get_args(annotation)
        nullable = is_union(annotation) and type(None) in args
        for arg in args:
            yield from nullable_occurrences(arg, target, nullable)

    def normalize_nullable(value: Any, validate: Callable[[Any], Any]) -> Any:
        try:
            return validate(value)
        except ValidationError as exc:
            details = exc.errors(include_url=False)
            if len(details) == 1 and not details[0]['loc'] and details[0]['type'] == 'vitya_empty':
                return None
            raise

    def allows_empty(field_type: Type[Any], handler: Any) -> bool:
        # The inner schema hook receives T for both T and Optional[T]. Only the
        # enclosing field has the annotation that distinguishes these cases.
        generator = getattr(handler, '_generate_schema', None)
        stack = getattr(generator, 'model_type_stack', None)
        model = stack.get() if stack is not None else None
        fields = getattr(model, 'model_fields', {})
        field = fields.get(getattr(handler, 'field_name', None))
        if field is None:
            return False
        # A repeated type can occupy both required and nullable slots in a tuple.
        # Keep required slots strict; Nullable[T] marks the individual nullable slot.
        return set(nullable_occurrences(field.annotation, field_type)) == {True}

    def field_schema(cls: Type[Any], validate: Callable[[Any], Any], handler: Any) -> 'core_schema.CoreSchema':
        primitive = next((t for t in cls.__mro__ if t in (str, int, Decimal, float)), Any)
        return core_schema.no_info_wrap_validator_function(
            lambda value, _handler: validate(value), handler.generate_schema(primitive),
        )
