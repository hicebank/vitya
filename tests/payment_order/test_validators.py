from decimal import Decimal
from typing import Optional, Type

import pytest

from tests.payment_order.testdata import INVALID_UIN, IP_ACCOUNT, VALID_UIN
from vitya.payment_order.errors import (
    AccountNumberValidationSizeError,
    AccountNumberValidationTypeError,
    AmountValidationLengthError,
    AmountValidationLessOrEqualZeroError,
    NumberValidationLenError,
    OperationKindValidationTypeError,
    OperationKindValidationValueError,
    PayeeValidationNameError,
    PayeeValidationSizeError,
    PayerValidationSizeError,
    PaymentOrderValidationError,
    PurposeCodeValidationTypeError,
    PurposeValidationCharactersError,
    PurposeValidationMaxLenError,
    PurposeValidationTypeError,
    UINValidationControlSumError,
    UINValidationDigitsOnlyError,
    UINValidationLenError,
    UINValidationOnlyZeroError,
    UINValidationTypeError,
)
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


@pytest.mark.parametrize(
    'value, exception, expected_value',
    [
        ('000001', None, Decimal('000001')),
        ('1' * 19, AmountValidationLengthError, None),
        ('0', AmountValidationLessOrEqualZeroError, None),
        ('-0.01', AmountValidationLessOrEqualZeroError, None),
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
        ('Ashot Ashot', None, 'Ashot Ashot'),
        ('', PayerValidationSizeError, None),
        ('0' * 161, PayerValidationSizeError, None),
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
        ('Ashot Ashot', None, 'Ashot Ashot'),
        ('', PayeeValidationSizeError, None),
        ('0' * 161, PayeeValidationSizeError, None),
        ('with 40802810722200035222', PayeeValidationNameError, None),
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
        ('1', None, 1),
        ('', None, 5),
        (None, None, 5),
        ('a', PaymentOrderValidationError, None),
        ('6', PaymentOrderValidationError, None),
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


@pytest.mark.parametrize(
    'value, exception, expected_value',
    [
        (1, AccountNumberValidationTypeError, None),
        ('', AccountNumberValidationSizeError, None),
        ('1' * 21, AccountNumberValidationSizeError, None),
        (IP_ACCOUNT, None, IP_ACCOUNT),
    ]
)
def test_validate_account_number(
    value: str,
    exception: Optional[Type[Exception]],
    expected_value: Optional[int]
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_account_number(value=value)
    else:
        assert validate_account_number(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception, expected_value',
    [
        (None, OperationKindValidationTypeError, None),
        (1, OperationKindValidationTypeError, None),
        ('', OperationKindValidationValueError, None),
        ('1' * 3, OperationKindValidationValueError, None),
        ('02', None, '02'),
    ]
)
def test_validate_operation_kind(
    value: str,
    exception: Optional[Type[Exception]],
    expected_value: Optional[int]
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_operation_kind(value=value)
    else:
        assert validate_operation_kind(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception, expected_value',
    [
        (None, UINValidationTypeError, None),
        (1, UINValidationTypeError, None),
        ('', None, None),
        ('111', UINValidationLenError, None),
        ('0000', UINValidationOnlyZeroError, None),
        ('aaaa', UINValidationDigitsOnlyError, None),
        (INVALID_UIN, UINValidationControlSumError, None),
        (VALID_UIN, None, VALID_UIN),
    ]
)
def test_validate_uin(
    value: str,
    exception: Optional[Type[Exception]],
    expected_value: Optional[int]
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_uin(value=value)
    else:
        assert validate_uin(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception, expected_value',
    [
        ('a', PurposeCodeValidationTypeError, None),
        (1, None, 1)
    ]
)
def test_validate_purpose_code(
    value: int,
    exception: Optional[Type[Exception]],
    expected_value: Optional[int]
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_purpose_code(value=value)
    else:
        assert validate_purpose_code(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception, expected_value',
    [
        (None, PurposeValidationTypeError, None),
        ('', None, '0'),
        ('1' * 211, PurposeValidationMaxLenError, None),
        ('的', PurposeValidationCharactersError, None),
        ('some', None, 'some'),
    ]
)
def test_validate_purpose(
    value: str,
    exception: Optional[Type[Exception]],
    expected_value: Optional[int]
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_purpose(value=value)
    else:
        assert validate_purpose(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception, expected_value',
    [
        ('000001', None, '000001'),
        ('0000011', NumberValidationLenError, None),
    ]
)
def test_validate_number(
    value: str,
    exception: Optional[Type[Exception]],
    expected_value: str
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_number(value=value)
    else:
        assert validate_number(value=value) == expected_value
