from decimal import Decimal
from typing import Optional, Type

import pytest

from vitya.payment_order.errors import (
    AmountValidationEqualZeroError,
    AmountValidationLengthError,
    PayeeValidationNameError,
    PayerValidationSizeError,
    PaymentOrderValidationError,
)
from vitya.payment_order.validators import (
    validate_amount,
    validate_payee,
    validate_payer,
    validate_payment_order,
)


@pytest.mark.parametrize(
    'value, exception, expected_value',
    [
        (
            '000001',
            None,
            Decimal('000001'),
        ),
        (
            '1' * 19,
            AmountValidationLengthError,
            None,
        ),
        (
            '0',
            AmountValidationEqualZeroError,
            None,
        ),
    ]
)
def test_validate_amount(
    value: str,
    exception: Optional[Type[Exception]],
    expected_value: Optional[str]
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_amount(amount=value)
    else:
        assert validate_amount(amount=value) == expected_value


@pytest.mark.parametrize(
    'value, exception, expected_value',
    [
        (
            'Ashot Ashot',
            None,
            'Ashot Ashot',
        ),
        (
            '',
            PayerValidationSizeError,
            None,
        ),
        (
            '0' * 161,
            PayerValidationSizeError,
            None,
        ),
    ]
)
def test_validate_payer(
    value: str,
    exception: Optional[Type[Exception]],
    expected_value: Optional[str]
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_payer(value=value)
    else:
        assert validate_payer(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception, expected_value',
    [
        (
            'Ashot Ashot',
            None,
            'Ashot Ashot',
        ),
        (
            '',
            PayerValidationSizeError,
            None,
        ),
        (
            '0' * 161,
            PayerValidationSizeError,
            None,
        ),
        (
            'some name with account 40802810722200035222',
            PayeeValidationNameError,
            None,
        ),
    ]
)
def test_validate_payee(
    value: str,
    exception: Optional[Type[Exception]],
    expected_value: Optional[str]
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_payee(value=value)
    else:
        assert validate_payee(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception, expected_value',
    [
        (
            '1',
            None,
            1,
        ),
        (
            '',
            None,
            5,
        ),
        (
            None,
            None,
            5,
        ),
        (
            'a',
            PaymentOrderValidationError,
            None,
        ),
        (
            '6',
            PaymentOrderValidationError,
            None,
        ),
    ]
)
def test_validate_payment_order(
    value: str,
    exception: Optional[Type[Exception]],
    expected_value: Optional[int]
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_payment_order(value=value)
    else:
        assert validate_payment_order(value=value) == expected_value
