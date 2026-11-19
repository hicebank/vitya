from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Generator, Optional, TypeVar

from ._pydantic import PYDANTIC_V2, PydanticValueError
from .validators import (
    ValidationError,
    validate_bic,
    validate_inn,
    validate_inn_ip,
    validate_inn_le,
    validate_kpp,
    validate_ogrn,
    validate_ogrnip,
    validate_oktmo,
    validate_snils,
)

if PYDANTIC_V2:
    from pydantic import WrapValidator
    from pydantic_core import PydanticCustomError, core_schema
    from typing_extensions import Annotated

    from ._pydantic_v2 import field_schema, normalize_nullable
else:
    from pydantic.errors import MissingError
    from pydantic.fields import ModelField

_T = TypeVar('_T')
if TYPE_CHECKING or not PYDANTIC_V2:
    Nullable = Optional[_T]
else:
    Nullable = Annotated[Optional[_T], WrapValidator(normalize_nullable)]


CallableGenerator = Generator[Callable[..., Any], None, None]


class PydanticValidationError(PydanticValueError):
    msg_template = 'invalid {name}: {reason}'

    if PYDANTIC_V2:
        def __init__(self, name: str, reason: str) -> None:
            super().__init__(self.msg_template.format(name=name, reason=reason))


class EmptyError(Exception):
    pass


def _validate_wrapper(func: Callable[[str], None], name: str, value: str) -> str:
    try:
        func(value)
    except ValidationError as e:
        raise PydanticValidationError(name=name, reason=str(e))

    return value


class FieldMixin(ABC):
    def __new__(cls, value: Any) -> 'FieldMixin':
        if type(value) is cls:
            return value
        value = cls._validate(value)
        if value is None:
            raise EmptyError
        return super().__new__(cls, value)  # type: ignore

    @classmethod
    @abstractmethod
    def _validate(cls, value: Any) -> Any:
        pass

    if PYDANTIC_V2:
        @classmethod
        def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> core_schema.CoreSchema:
            def validate(value: Any, allows_empty: Callable[[], bool]) -> Any:
                if value is None:
                    raise PydanticCustomError('none_not_allowed', 'none is not an allowed value')
                try:
                    return cls(value)
                except EmptyError:
                    if allows_empty():
                        return None
                    raise PydanticCustomError('vitya_empty', 'field required')
                except (ValueError, TypeError) as exc:
                    # Preserve the domain exception used to build localized field alerts.
                    raise PydanticCustomError('vitya', '{message}', {'message': str(exc), 'error': exc}) from exc

            return field_schema(cls, validate, handler)
    else:
        @classmethod
        def __get_validators__(cls) -> CallableGenerator:
            def validator(value: Any, field: 'ModelField') -> Any:
                try:
                    return cls(value)
                except EmptyError:
                    if field.allow_none:
                        return None
                    raise MissingError
            yield validator


class INN(FieldMixin, str):
    @classmethod
    def _validate(cls, value: str) -> Optional[str]:
        return validate_inn(value)


class INNIP(FieldMixin, str):
    @classmethod
    def _validate(cls, value: str) -> Optional[str]:
        return validate_inn_ip(value)


class INNLE(FieldMixin, str):
    @classmethod
    def _validate(cls, value: str) -> Optional[str]:
        return validate_inn_le(value)


class KPP(FieldMixin, str):
    @classmethod
    def _validate(cls, value: str) -> Optional[str]:
        return validate_kpp(value)


class BIC(FieldMixin, str):
    @classmethod
    def _validate(cls, value: str) -> str:
        return validate_bic(value)


class OGRN(FieldMixin, str):
    @classmethod
    def _validate(cls, value: str) -> str:
        return _validate_wrapper(validate_ogrn, 'ogrn', value)


class OGRNIP(FieldMixin, str):
    @classmethod
    def _validate(cls, value: str) -> str:
        return _validate_wrapper(validate_ogrnip, 'ogrn_ip', value)


class SNILS(FieldMixin, str):
    @classmethod
    def _validate(cls, value: str) -> str:
        return _validate_wrapper(validate_snils, 'snils', value)


class OKTMO(FieldMixin, str):
    @classmethod
    def _validate(cls, value: str) -> Optional[str]:
        return validate_oktmo(value)


# Pydantic strip NewType from ModelField.type_

class BoolWrapper:
    __slots__ = ('_value', )

    def __init__(self, value: bool):
        self._value = value

    def __bool__(self) -> bool:
        return self._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __eq__(self, other: Any) -> Any:
        if isinstance(other, type(self)):
            return self._value == other._value
        if isinstance(other, bool):
            return self._value == other
        return NotImplemented

    if PYDANTIC_V2:
        @classmethod
        def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> core_schema.CoreSchema:
            def validate(value: Any, _handler: Any) -> Any:
                if isinstance(value, cls):
                    return value
                if isinstance(value, bool):
                    return cls(value)
                raise PydanticCustomError('bool_type', 'value is not a valid boolean')

            return core_schema.no_info_wrap_validator_function(
                validate,
                core_schema.bool_schema(),
                serialization=core_schema.plain_serializer_function_ser_schema(
                    bool, return_schema=core_schema.bool_schema(), when_used='json',
                ),
            )

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        def validator(value: Any) -> Any:
            if isinstance(value, bool):
                return cls(value)
            if isinstance(value, cls):
                return value
            raise TypeError

        yield validator
