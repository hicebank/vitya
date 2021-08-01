from typing import Any, Callable, Generator

from .validators import (
    ValidationError,
    validate_bic,
    validate_inn,
    validate_inn_ip,
    validate_inn_jur,
    validate_kpp,
    validate_ogrn,
    validate_ogrnip,
    validate_oktmo,
    validate_snils,
)

try:
    from pydantic.errors import PydanticValueError
except ImportError:
    pass

CallableGenerator = Generator[Callable[..., Any], None, None]


class PydanticValidationError(PydanticValueError):
    msg_template = 'invalid {name}: {reason}'


def _validate_wrapper(func: Callable[[str], None], name: str, value: str) -> str:
    try:
        func(value)
    except ValidationError as e:
        raise PydanticValidationError(name=name, reason=str(e))

    return value


class Inn(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return _validate_wrapper(validate_inn, "inn", value)


class InnIp(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return _validate_wrapper(validate_inn_ip, "inn_ip", value)


class InnJur(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return _validate_wrapper(validate_inn_jur, "inn_jur", value)


class Kpp(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return _validate_wrapper(validate_kpp, "kpp", value)


class Bic(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return _validate_wrapper(validate_bic, "bic", value)


class Ogrn(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return _validate_wrapper(validate_ogrn, "ogrn", value)


class OgrnIp(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return _validate_wrapper(validate_ogrnip, "ogrn_ip", value)


class Snils(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return _validate_wrapper(validate_snils, "snils", value)


class Oktmo(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return _validate_wrapper(validate_oktmo, "oktmo", value)
