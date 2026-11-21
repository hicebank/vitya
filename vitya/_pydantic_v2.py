"""Core-schema helpers for Pydantic 2."""
from contextlib import contextmanager
from contextvars import ContextVar
from decimal import Decimal
from functools import lru_cache, wraps
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    cast,
    get_args,
    get_origin,
)

from ._pydantic import PYDANTIC_V2
from .typing_helpers import is_union

if PYDANTIC_V2:
    from pydantic.fields import FieldInfo
    from pydantic_core import (
        PydanticCustomError,
        PydanticUndefined,
        ValidationError,
        core_schema,
    )
    from typing_extensions import Annotated

    def unwrap_field_type(annotation: Any) -> Any:
        if get_origin(annotation) is Annotated:
            return unwrap_field_type(get_args(annotation)[0])
        if hasattr(annotation, '__supertype__'):  # NewType, including nested aliases
            return unwrap_field_type(annotation.__supertype__)
        return annotation

    def apply_optional_defaults(model: Type[Any]) -> None:
        for field in model.model_fields.values():
            annotation = unwrap_field_type(field.annotation)
            if not (field.is_required() and is_union(annotation) and type(None) in get_args(annotation)):
                continue
            # A bare Optional had an implicit None in v1. Field(...) and other
            # explicitly assigned fields must keep the requiredness chosen by the caller.
            if getattr(field, '_original_assignment', ...) is not PydanticUndefined:
                continue
            original = field._original_annotation
            if get_origin(original) is Annotated and any(isinstance(m, FieldInfo) for m in get_args(original)[1:]):
                continue
            field.default = None

    def with_checker_error(exc: ValidationError, checker_error: PydanticCustomError, value: Any) -> ValidationError:
        # The pickle protocol retains the original PydanticCustomError objects
        # (including their templates), input mode and hide_input flag. errors()
        # only exposes rendered messages and string codes shared with built-in errors.
        _, args = cast(Tuple[Any, Tuple[Any, ...]], exc.__reduce__())
        title, errors, input_type, hide_input = args
        for error in errors:
            # Older core versions pickle custom errors as rendered details.
            if isinstance(error['type'], str) and 'url' not in error:
                error['type'] = PydanticCustomError(error['type'], error['msg'], error.get('ctx'))
        errors.append({'type': checker_error, 'loc': (), 'input': value})
        return ValidationError.from_exception_data(title, errors, input_type, hide_input)

    class _ParsedFields:
        def __init__(self) -> None:
            self.data: Optional[Dict[str, Any]] = None
            self.defaults: Dict[str, Any] = {}
            self.failed_values: Optional[Dict[str, Any]] = None
            self.complete = False

    _active: ContextVar[_ParsedFields] = ContextVar('vitya_parsed_fields')

    @contextmanager
    def capture_fields() -> Iterator[_ParsedFields]:
        partial = _ParsedFields()
        token = _active.set(partial)
        try:
            yield partial
        finally:
            _active.reset(token)

    def observe_model_fields(schema: Any, model: Type[Any]) -> None:
        # A wrap model_validator only gets a model if every field succeeded.
        # Capture the values already parsed by core for the failure path.
        parent = schema
        while parent['schema']['type'] != 'model-fields':
            parent = parent['schema']
        fields_schema = parent['schema']
        metadata = fields_schema.setdefault('metadata', {})
        if metadata.get('vitya_fields_observed'):
            return  # Pydantic reuses the same schema when nesting an existing model.
        metadata['vitya_fields_observed'] = True
        static_defaults: List[str] = []

        def observe(value: Any, info: core_schema.ValidationInfo) -> Any:
            # This is the live dictionary to which core adds each successful field,
            # including fields processed after the first error.
            _active.get().data = info.data
            return value

        def observe_factory(name: str, factory: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(factory)
            def wrapped(*args: Any) -> Any:
                value = factory(*args)
                partial = _active.get(None)
                if partial is not None and partial.data is None:
                    partial.defaults[name] = value
                return value
            return wrapped

        for name, field in fields_schema['fields'].items():
            inner = field
            default = field['schema']
            if default['type'] == 'default':
                inner = default
                if 'default_factory' in default:
                    default['default_factory'] = observe_factory(name, default['default_factory'])
                elif 'default' in default:
                    static_defaults.append(name)
            inner['schema'] = core_schema.with_info_before_validator_function(observe, inner['schema'])

        def validate(value: Any, handler: core_schema.ValidatorFunctionWrapHandler) -> Any:
            partial = _active.get()
            try:
                result = handler(value)
            except ValidationError as exc:
                details = exc.errors(include_url=False)
                if not all(detail['loc'] for detail in details):
                    raise
                # When every field was omitted, core may only have evaluated
                # defaults. Never replay a service validator or default factory.
                values = partial.data
                if values is None:
                    values = {name: model.model_fields[name].get_default() for name in static_defaults}
                    values.update(partial.defaults)
                partial.failed_values = values
                raise
            partial.complete = True
            return result

        parent['schema'] = core_schema.no_info_wrap_validator_function(validate, fields_schema)

    def _nullable_slot(schema: Any, validator: Callable[..., Any], nullable: bool = False) -> bool:
        if isinstance(schema, (list, tuple)):
            return any(_nullable_slot(item, validator, nullable) for item in schema)
        if not isinstance(schema, dict):
            return False
        kind = schema.get('type')
        if kind == 'function-wrap' and schema['function']['function'] is validator:
            return nullable
        # Wrappers and union alternatives validate the same input. A collection
        # itself being nullable says nothing about its keys, values or items.
        for key in ('schema', 'choices', 'steps', 'json_schema', 'python_schema', 'lax_schema', 'strict_schema'):
            if key in schema and _nullable_slot(schema[key], validator, nullable or kind == 'nullable'):
                return True
        for key in ('items_schema', 'keys_schema', 'values_schema', 'definitions'):
            if key in schema and _nullable_slot(schema[key], validator):
                return True
        fields = schema.get('fields', {})
        return isinstance(fields, dict) and any(_nullable_slot(field, validator) for field in fields.values())

    def normalize_nullable(value: Any, validate: Callable[[Any], Any]) -> Any:
        try:
            return validate(value)
        except ValidationError as exc:
            details = exc.errors(include_url=False)
            if len(details) == 1 and not details[0]['loc'] and details[0]['type'] == 'vitya_empty':
                return None
            raise

    def field_schema(
        cls: Type[Any], validate: Callable[[Any, Callable[[], bool]], Any], handler: Any,
    ) -> 'core_schema.CoreSchema':
        # The leaf hook receives T for both T and Optional[T]. Its own callback
        # identifies this exact occurrence in the completed model schema.
        generator = getattr(handler, '_generate_schema', None)
        # The builder fills these definitions after the leaf hook returns.
        # Keep this generation's schemas, so existing TypeAdapters also work
        # after their model is rebuilt.
        definitions = getattr(getattr(generator, 'defs', None), '_definitions', {})

        @lru_cache(maxsize=1)
        def allows_empty() -> bool:
            return any(_nullable_slot(schema, validate_slot) for schema in definitions.values())

        def validate_slot(value: Any, _handler: Any) -> Any:
            return validate(value, allows_empty)

        primitive = next((t for t in cls.__mro__ if t in (str, int, Decimal, float)), Any)
        return core_schema.no_info_wrap_validator_function(validate_slot, handler.generate_schema(primitive))
