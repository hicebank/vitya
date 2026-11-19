"""Core-schema helpers for Pydantic 2."""
from contextvars import ContextVar
from decimal import Decimal
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Type,
    get_args,
    get_origin,
)

from ._pydantic import PYDANTIC_V2
from .typing_helpers import is_union

if PYDANTIC_V2:
    from pydantic_core import (
        ErrorDetails,
        InitErrorDetails,
        PydanticCustomError,
        ValidationError,
        core_schema,
    )
    from typing_extensions import Annotated

    def unwrap_annotated(annotation: Any) -> Any:
        if get_origin(annotation) is Annotated:
            return get_args(annotation)[0]
        return annotation

    def _line_error(detail: ErrorDetails) -> InitErrorDetails:
        # from_exception_data accepts built-in codes, but needs the error object
        # for custom codes, including those supplied by a consuming service.
        code = detail['type']
        error: InitErrorDetails = {'type': code, 'loc': detail['loc'], 'input': detail['input']}
        if code not in get_args(core_schema.ErrorType):
            error['type'] = PydanticCustomError(code, detail['msg'], detail.get('ctx'))
        if 'ctx' in detail:
            error['ctx'] = detail['ctx']
        return error

    class _ParsedFields:
        def __init__(self) -> None:
            self.data: Optional[Dict[str, Any]] = None
            self.defaults: Dict[str, Any] = {}

    def check_model_fields(schema: Any, model: Type[Any], check: Callable[[Dict[str, Any]], Any]) -> None:
        # Work inside the model, before pydantic-core commits a validated assignment.
        parent = schema
        while parent['schema']['type'] != 'model-fields':
            parent = parent['schema']
        fields_schema = parent['schema']
        active: ContextVar[_ParsedFields] = ContextVar('parsed_fields')
        static_defaults: List[str] = []

        def observe(value: Any, info: core_schema.ValidationInfo) -> Any:
            # This is the live dictionary to which core adds each successful field,
            # including fields processed after the first error.
            active.get().data = info.data
            return value

        def observe_factory(name: str, factory: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(factory)
            def wrapped(*args: Any) -> Any:
                value = factory(*args)
                partial = active.get(None)
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

        def validate(value: Any, handler: core_schema.ValidatorFunctionWrapHandler, info: core_schema.ValidationInfo) -> Any:
            partial = _ParsedFields()
            token = active.set(partial)
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
                try:
                    check(values)
                except PydanticCustomError as checker_error:
                    errors: List[InitErrorDetails] = [_line_error(detail) for detail in details]
                    errors.append({'type': checker_error, 'loc': (), 'input': value})
                    raise ValidationError.from_exception_data(
                        exc.title, errors, input_type='json' if info.mode == 'json' else 'python',
                        hide_input=model.model_config.get('hide_input_in_errors', False),
                    ) from None
                raise
            finally:
                active.reset(token)
            check(result[0])
            return result

        parent['schema'] = core_schema.with_info_wrap_validator_function(validate, fields_schema)

    def nullable_occurrences(annotation: Any, target: Type[Any], nullable: bool = False) -> Iterator[bool]:
        annotation = unwrap_annotated(annotation)
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
