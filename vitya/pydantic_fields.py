from abc import ABC, abstractmethod
from typing import Any, Callable, Generator, Optional

from pydantic.fields import ModelField

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

try:
    from pydantic.errors import MissingError, PydanticValueError
except ImportError:  # pragma: no cover
    pass

CallableGenerator = Generator[Callable[..., Any], None, None]


class PydanticValidationError(PydanticValueError):
    msg_template = 'invalid {name}: {reason}'


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
        if type(value) == cls:
            return value  # type: ignore
        value = cls._validate(value)
        if value is None:
            raise EmptyError
        return super().__new__(cls, value)  # type: ignore

    @classmethod
    @abstractmethod
    def _validate(cls, value: Any) -> Any:
        pass

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        def validator(value: Any, field: ModelField) -> Any:
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

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        def validator(value: Any) -> Any:
            if isinstance(value, bool):
                return cls(value)
            if isinstance(value, cls):
                return value
            raise TypeError

        yield validator
