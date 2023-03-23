from decimal import Decimal
from typing import Any, Callable, Generator, Optional

from vitya.payment_order.validators import (
    validate_account_number,
    validate_amount,
    validate_number,
    validate_operation_kind,
    validate_payee,
    validate_payer,
    validate_payer_status,
    validate_payment_order,
    validate_purpose,
    validate_purpose_code,
    validate_uin,
)

CallableGenerator = Generator[Callable[..., Any], None, None]


class Number(str):
    """Номер платёжного поручения (3)"""

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return validate_number(value)


class Amount(Decimal):
    """Сумма (7)"""

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
    """Плательщик (8)"""


class Payee(Customer):
    """Наименование получателя (16)"""

    @classmethod
    def validate(cls, value: str) -> str:
        return validate_payee(value)


class PaymentOrder(int):
    """Очерёдность платежа (21)"""

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> int:
        return validate_payment_order(value)


class AccountNumber(str):
    """Счёт"""

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return validate_account_number(value)


class OperationKind(str):
    """Вид операции (18)"""

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return validate_operation_kind(value)


class UIN(str):
    """Код (УИН) (22)"""

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> Optional[str]:
        return validate_uin(value)


class PurposeCode(int):
    """Назначение платежа кодовое (20)"""

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: int) -> int:
        return validate_purpose_code(value)


class Purpose(str):
    """Назначение платежа (24)"""

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return validate_purpose(value)


class PayerStatus(str):
    """Статус плательщика (101)"""

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        return validate_payer_status(value)
