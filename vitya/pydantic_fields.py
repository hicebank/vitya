from vitya import validate_inn, ValidationError, validate_kpp, validate_bic, validate_ogrn

# TODO: add tests


try:
    from pydantic import PydanticValueError
    from pydantic.typing import CallableGenerator
except ImportError:
    pass


class Inn(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str):
        try:
            validate_inn(value)
        except ValidationError as e:
            raise PydanticValueError() from e

        return value


class Kpp(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str):
        try:
            validate_kpp(value)
        except ValidationError as e:
            raise PydanticValueError() from e

        return value


class Bic(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str):
        try:
            validate_bic(value)
        except ValidationError as e:
            raise PydanticValueError() from e

        return value


class Ogrn(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str):
        try:
            validate_ogrn(value)
        except ValidationError as e:
            raise PydanticValueError() from e

        return value
