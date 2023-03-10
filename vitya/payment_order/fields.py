from decimal import Decimal
from typing import Any, Callable, Generator

from vitya.payment_order.validators import (
    validate_amount,
    validate_payee,
    validate_payer,
    validate_payment_order,
)

CallableGenerator = Generator[Callable[..., Any], None, None]


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
