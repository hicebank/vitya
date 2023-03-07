from decimal import Decimal
from typing import Any, Callable, Generator, Optional

from vitya.payment_order.validators import (
    validate_account_number,
    validate_amount,
    validate_number,
    validate_operation_kind,
    validate_payee,
    validate_payer,
    validate_payment_order,
    validate_purpose,
    validate_purpose_code,
    validate_uin,
)

CallableGenerator = Generator[Callable[..., Any], None, None]


class Number(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return validate_number(value)


class Amount(Decimal):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> Decimal:
        return validate_amount(value)


class Customer(str):
    """Общий класс для описания сущности владельца денег"""

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return validate_payer(value)


class Payer(Customer):
    """Плательщик"""


class Payee(Customer):
    """Получатель (в названии должен содержать счета)"""

    @classmethod
    def validate(cls, value: str) -> str:
        return validate_payee(value)


class PaymentOrder(int):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> int:
        return validate_payment_order(value)


class AccountNumber(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return validate_account_number(value)


class OperationKind(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return validate_operation_kind(value)


class UIN(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> Optional[str]:
        return validate_uin(value)


class PurposeCode(int):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: int) -> int:
        return validate_purpose_code(value)


class Purpose(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return validate_purpose(value)
