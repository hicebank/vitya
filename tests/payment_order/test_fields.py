from typing import Type

import pytest
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError
from pydantic.errors import Decimal

from tests.payment_order.testdata import INVALID_UIN, IP_ACCOUNT, VALID_UIN
from vitya.payment_order.errors import (
    AccountNumberValidationDigitsOnlyError,
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
    UINValidationControlSumError,
    UINValidationDigitsOnlyError,
    UINValidationLenError,
    UINValidationOnlyZeroError,
    UINValidationTypeError,
)
from vitya.payment_order.fields import (
    AccountNumber,
    Amount,
    Number,
    OperationKind,
    Payee,
    Payer,
    PaymentOrder,
    Purpose,
    PurposeCode,
    Uin,
)


class TestNumberModel(BaseModel):
    field: Number


@pytest.mark.parametrize(
    'value, exception, expected',
    [
        ('000001', None, '000001'),
        ('0000011', NumberValidationLenError, None),
    ]
)
def test_number(
    value: str,
    exception: Type[Exception],
    expected: str,
) -> None:
    try:
        assert TestNumberModel(field=value).field == expected
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc, exception)


class TestAmountModel(BaseModel):
    field: Amount


@pytest.mark.parametrize(
    'value, exception, expected',
    [
        ('000001', None, Decimal('000001')),
        ('1' * 19, AmountValidationLengthError, None),
        ('0', AmountValidationLessOrEqualZeroError, None),
        ('-0.01', AmountValidationLessOrEqualZeroError, None),
    ]
)
def test_amount(
    value: str,
    exception: Type[Exception],
    expected: str,
) -> None:
    try:
        assert TestAmountModel(field=value).field == expected
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc, exception)


class TestPayerModel(BaseModel):
    field: Payer


@pytest.mark.parametrize(
    'value, exception, expected',
    [
        ('Ashot Ashot', None, 'Ashot Ashot'),
        ('', PayerValidationSizeError, None),
        ('0' * 161, PayerValidationSizeError, None),
    ]
)
def test_payer(
    value: str,
    exception: Type[Exception],
    expected: str,
) -> None:
    try:
        assert TestPayerModel(field=value).field == expected
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc, exception)


class TestPayeeModel(BaseModel):
    field: Payee


@pytest.mark.parametrize(
    'value, exception, expected',
    [
        ('Ashot Ashot', None, 'Ashot Ashot'),
        ('', PayeeValidationSizeError, None),
        ('0' * 161, PayeeValidationSizeError, None),
        ('with 40802810722200035222', PayeeValidationNameError, None),
    ]
)
def test_payee(
    value: str,
    exception: Type[Exception],
    expected: str,
) -> None:
    try:
        assert TestPayeeModel(field=value).field == expected
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc, exception)


class TestPaymentOrderModel(BaseModel):
    field: PaymentOrder


@pytest.mark.parametrize(
    'value, exception, expected',
    [
        ('1', None, 1),
        ('', None, 5),
        ('a', PaymentOrderValidationError, None),
        ('6', PaymentOrderValidationError, None),
    ]
)
def test_payment_order(
    value: str,
    exception: Type[Exception],
    expected: str,
) -> None:
    try:
        assert TestPaymentOrderModel(field=value).field == expected
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc, exception)


class TestAccountNumberModel(BaseModel):
    field: AccountNumber


@pytest.mark.parametrize(
    'value, exception, expected',
    [
        (1, AccountNumberValidationTypeError, None),
        ('', AccountNumberValidationSizeError, None),
        ('1' * 21, AccountNumberValidationSizeError, None),
        ('a' * 20, AccountNumberValidationDigitsOnlyError, None),
        (IP_ACCOUNT, None, IP_ACCOUNT),
    ]
)
def test_account_number(
    value: str,
    exception: Type[Exception],
    expected: str,
) -> None:
    try:
        assert TestAccountNumberModel(field=value).field == expected
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc, exception)


class TestOperationKindModel(BaseModel):
    field: OperationKind


@pytest.mark.parametrize(
    'value, exception, expected',
    [
        (1, OperationKindValidationTypeError, None),
        ('', OperationKindValidationValueError, None),
        ('1' * 3, OperationKindValidationValueError, None),
        ('02', None, '02'),
    ]
)
def test_operation_kind(
    value: str,
    exception: Type[Exception],
    expected: str,
) -> None:
    try:
        assert TestOperationKindModel(field=value).field == expected
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc, exception)


class TestUINModel(BaseModel):
    field: Uin


@pytest.mark.parametrize(
    'value, exception, expected',
    [
        (1, UINValidationTypeError, None),
        ('', None, None),
        ('111', UINValidationLenError, None),
        ('0000', UINValidationOnlyZeroError, None),
        ('aaaa', UINValidationDigitsOnlyError, None),
        (INVALID_UIN, UINValidationControlSumError, None),
        (VALID_UIN, None, VALID_UIN),
    ]
)
def test_uin(
    value: str,
    exception: Type[Exception],
    expected: str,
) -> None:
    try:
        assert TestUINModel(field=value).field == expected
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc, exception)


class TestPurposeCodeModel(BaseModel):
    field: PurposeCode


@pytest.mark.parametrize(
    'value, exception, expected',
    [
        ('a', PurposeCodeValidationTypeError, None),
        (1, None, 1)
    ]
)
def test_purpose_code(
    value: str,
    exception: Type[Exception],
    expected: str,
) -> None:
    try:
        assert TestPurposeCodeModel(field=value).field == expected
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc, exception)


class TestPurposeModel(BaseModel):
    field: Purpose


@pytest.mark.parametrize(
    'value, exception, expected',
    [
        ('', None, '0'),
        ('1' * 211, PurposeValidationMaxLenError, None),
        ('的', PurposeValidationCharactersError, None),
        ('some', None, 'some'),
    ]
)
def test_purpose(
    value: str,
    exception: Type[Exception],
    expected: str,
) -> None:
    try:
        assert TestPurposeModel(field=value).field == expected
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc, exception)