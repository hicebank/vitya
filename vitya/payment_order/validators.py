import re
from decimal import Decimal

from vitya.payment_order.errors import (
    AmountValidationEqualZeroError,
    AmountValidationLengthError,
    PayeeValidationNameError,
    PayerValidationSizeError,
    PaymentOrderValidationError,
)


def validate_amount(amount: str) -> Decimal:
    if isinstance(amount, str):
        if len(amount) > 18:
            raise AmountValidationLengthError

    value = Decimal(amount)
    if value == Decimal(0.0):
        raise AmountValidationEqualZeroError

    return value


def validate_payer(value: str) -> str:
    len_value = len(value)
    if len_value < 1 or len_value > 160:
        raise PayerValidationSizeError
    return value


def validate_payee(value: str) -> str:
    validate_payer(value)
    if bool(re.match('(.*)(4)[0-9]{19}', value)):
        raise PayeeValidationNameError
    return value


def validate_payment_order(value: str) -> int:
    if value is None or value == '':
        return 5

    try:
        value_int = int(value)
    except ValueError:
        raise PaymentOrderValidationError
    if value_int not in {1, 2, 3, 4, 5}:
        raise PaymentOrderValidationError
    return value_int
