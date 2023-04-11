from contextlib import nullcontext
from decimal import Decimal
from typing import ContextManager, Optional

import pytest

from tests.payment_order.testdata import INVALID_UIN, IP_ACCOUNT, VALID_CBC, VALID_UIN
from vitya.payment_order.errors import (
    AccountNumberValidationDigitsOnlyError,
    AccountNumberValidationSizeError,
    AccountNumberValidationTypeError,
    AmountValidationLengthError,
    AmountValidationLessOrEqualZeroError,
    CbcValidationTypeError,
    CbcValidationValueCannotZerosOnly,
    CbcValidationValueDigitsOnlyError,
    CbcValidationValueLenError,
    DocumentDateValidationTypeError,
    DocumentNumberValidationTypeError,
    NumberValidationLenError,
    OperationKindValidationTypeError,
    OperationKindValidationValueError,
    PayeeValidationNameError,
    PayeeValidationSizeError,
    PayerStatusValidationTypeError,
    PayerStatusValidationValueError,
    PayerValidationSizeError,
    PaymentOrderValidationError,
    PurposeCodeValidationTypeError,
    PurposeValidationCharactersError,
    PurposeValidationMaxLenError,
    PurposeValidationTypeError,
    ReasonValidationTypeError,
    ReasonValidationValueError,
    ReasonValidationValueLenError,
    TaxPeriodValidationTypeError,
    UINValidationControlSumError,
    UINValidationDigitsOnlyError,
    UINValidationLenError,
    UINValidationOnlyZeroError,
    UINValidationTypeError,
)
from vitya.payment_order.validators import (
    validate_account_number,
    validate_amount,
    validate_cbc,
    validate_document_date,
    validate_document_number,
    validate_number,
    validate_operation_kind,
    validate_payee,
    validate_payer,
    validate_payer_status,
    validate_payment_order,
    validate_purpose,
    validate_purpose_code,
    validate_reason,
    validate_tax_period,
    validate_uin,
    validate_uin_control_sum,
)


@pytest.mark.parametrize(
    'value, exception_handler, expected_value',
    [
        ('000001', nullcontext(), Decimal('000001')),
        ('1' * 19, pytest.raises(AmountValidationLengthError), None),
        ('0', pytest.raises(AmountValidationLessOrEqualZeroError), None),
        ('-0.01', pytest.raises(AmountValidationLessOrEqualZeroError), None),
    ]
)
def test_validate_amount(
    value: str,
    exception_handler: ContextManager,
    expected_value: Optional[str]
) -> None:
    with exception_handler:
        assert validate_amount(amount=value) == expected_value


@pytest.mark.parametrize(
    'value, exception_handler, expected_value',
    [
        ('Ashot Ashot', nullcontext(), 'Ashot Ashot'),
        ('', pytest.raises(PayerValidationSizeError), None),
        ('0' * 161, pytest.raises(PayerValidationSizeError), None),
    ]
)
def test_validate_payer(
    value: str,
    exception_handler: ContextManager,
    expected_value: Optional[str]
) -> None:
    with exception_handler:
        assert validate_payer(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception_handler, expected_value',
    [
        ('Ashot Ashot', nullcontext(), 'Ashot Ashot'),
        ('', pytest.raises(PayeeValidationSizeError), None),
        ('0' * 161, pytest.raises(PayeeValidationSizeError), None),
        ('with 40802810722200035222', pytest.raises(PayeeValidationNameError), None),
    ]
)
def test_validate_payee(
    value: str,
    exception_handler: ContextManager,
    expected_value: Optional[str]
) -> None:
    with exception_handler:
        assert validate_payee(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception_handler, expected_value',
    [
        ('1', nullcontext(), 1),
        ('', nullcontext(), 5),
        (None, nullcontext(), 5),
        ('a', pytest.raises(PaymentOrderValidationError), None),
        ('6', pytest.raises(PaymentOrderValidationError), None),
    ]
)
def test_validate_payment_order(
    value: str,
    exception_handler: ContextManager,
    expected_value: Optional[int]
) -> None:
    with exception_handler:
        assert validate_payment_order(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception_handler, expected_value',
    [
        (1, pytest.raises(AccountNumberValidationTypeError), None),
        ('', pytest.raises(AccountNumberValidationSizeError), None),
        ('1' * 21, pytest.raises(AccountNumberValidationSizeError), None),
        ('a' * 20, pytest.raises(AccountNumberValidationDigitsOnlyError), None),
        (IP_ACCOUNT, nullcontext(), IP_ACCOUNT),
    ]
)
def test_validate_account_number(
    value: str,
    exception_handler: ContextManager,
    expected_value: Optional[int]
) -> None:
    with exception_handler:
        assert validate_account_number(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception_handler, expected_value',
    [
        (None, pytest.raises(OperationKindValidationTypeError), None),
        (1, pytest.raises(OperationKindValidationTypeError), None),
        ('', pytest.raises(OperationKindValidationValueError), None),
        ('1' * 3, pytest.raises(OperationKindValidationValueError), None),
        ('02', nullcontext(), '02'),
    ]
)
def test_validate_operation_kind(
    value: str,
    exception_handler: ContextManager,
    expected_value: Optional[int]
) -> None:
    with exception_handler:
        assert validate_operation_kind(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception_handler, expected_value',
    [
        (None, pytest.raises(UINValidationTypeError), None),
        (1, pytest.raises(UINValidationTypeError), None),
        ('', nullcontext(), None),
        ('111', pytest.raises(UINValidationLenError), None),
        ('0000', pytest.raises(UINValidationOnlyZeroError), None),
        ('aaaa', pytest.raises(UINValidationDigitsOnlyError), None),
        (INVALID_UIN, pytest.raises(UINValidationControlSumError), None),
        (VALID_UIN, nullcontext(), VALID_UIN),
    ]
)
def test_validate_uin(
    value: str,
    exception_handler: ContextManager,
    expected_value: Optional[int]
) -> None:
    with exception_handler:
        assert validate_uin(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception_handler, expected_value',
    [
        ('a', pytest.raises(PurposeCodeValidationTypeError), None),
        (1, nullcontext(), 1)
    ]
)
def test_validate_purpose_code(
    value: int,
    exception_handler: ContextManager,
    expected_value: Optional[int]
) -> None:
    with exception_handler:
        assert validate_purpose_code(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception_handler, expected_value',
    [
        (None, pytest.raises(PurposeValidationTypeError), None),
        ('', nullcontext(), '0'),
        ('1' * 211, pytest.raises(PurposeValidationMaxLenError), None),
        ('的', pytest.raises(PurposeValidationCharactersError), None),
        ('some', nullcontext(), 'some'),
    ]
)
def test_validate_purpose(
    value: str,
    exception_handler: ContextManager,
    expected_value: Optional[int]
) -> None:
    with exception_handler:
        assert validate_purpose(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception_handler, expected_value',
    [
        ('000001', nullcontext(), '000001'),
        ('0000011', pytest.raises(NumberValidationLenError), None),
    ]
)
def test_validate_number(
    value: str,
    exception_handler: ContextManager,
    expected_value: str
) -> None:
    with exception_handler:
        assert validate_number(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception_handler',
    [
        ('a', pytest.raises(UINValidationDigitsOnlyError)),
        ('11111', nullcontext()),
        ('0' * 20, pytest.raises(UINValidationOnlyZeroError)),
        (INVALID_UIN, pytest.raises(UINValidationControlSumError)),
        (INVALID_UIN, pytest.raises(UINValidationControlSumError)),
        ('0' * 9 + '1' + '0' * 10, pytest.raises(UINValidationControlSumError)),
    ]
)
def test_validate_uin_control_sum(
    value: str,
    exception_handler: ContextManager
):
    with exception_handler:
        validate_uin_control_sum(value=value)


@pytest.mark.parametrize(
    'value, exception_handler, expected_value',
    [
        (None, pytest.raises(PayerStatusValidationTypeError), None),
        ('00', pytest.raises(PayerStatusValidationValueError), None),
        ('06', nullcontext(), '06'),
    ]
)
def test_validate_payer_status(
    value: str,
    exception_handler: ContextManager,
    expected_value: Optional[str]
) -> None:
    with exception_handler:
        assert validate_payer_status(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception_handler, expected_value',
    [
        (None, pytest.raises(CbcValidationTypeError), None),
        ('', nullcontext(), None),
        ('0', nullcontext(), None),
        ('1', pytest.raises(CbcValidationValueLenError), None),
        ('a' * 20, pytest.raises(CbcValidationValueDigitsOnlyError), None),
        ('0' * 20, pytest.raises(CbcValidationValueCannotZerosOnly), None),
        (VALID_CBC, nullcontext(), VALID_CBC),
    ]
)
def test_validate_cbc(
    value: str,
    exception_handler: ContextManager,
    expected_value: Optional[str]
) -> None:
    with exception_handler:
        assert validate_cbc(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception_handler, expected_value',
    [
        (None, pytest.raises(ReasonValidationTypeError), None),
        ('', nullcontext(), None),
        ('0', nullcontext(), None),
        ('АИИ', pytest.raises(ReasonValidationValueLenError), None),
        ('АИ', pytest.raises(ReasonValidationValueError), None),
        ('ПК', nullcontext(), 'ПК'),
    ]
)
def test_validate_reason(
    value: str,
    exception_handler: ContextManager,
    expected_value: Optional[str]
) -> None:
    with exception_handler:
        assert validate_reason(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception_handler, expected_value',
    [
        (None, pytest.raises(TaxPeriodValidationTypeError), None),
        ('', nullcontext(), None),
        ('0', nullcontext(), None),
        ('2022-01-20', nullcontext(), '2022-01-20'),
    ]
)
def test_validate_tax_period(
    value: str,
    exception_handler: ContextManager,
    expected_value: Optional[str]
) -> None:
    with exception_handler:
        assert validate_tax_period(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception_handler, expected_value',
    [
        (None, pytest.raises(DocumentNumberValidationTypeError), None),
        ('', nullcontext(), None),
        ('0', nullcontext(), None),
        ('03;', nullcontext(), '03;'),
    ]
)
def test_validate_document_number(
    value: str,
    exception_handler: ContextManager,
    expected_value: Optional[str]
) -> None:
    with exception_handler:
        assert validate_document_number(value=value) == expected_value


@pytest.mark.parametrize(
    'value, exception_handler, expected_value',
    [
        [None, pytest.raises(DocumentDateValidationTypeError), None],
        ('', nullcontext(), None),
        ('0', nullcontext(), None),
        ('20220202', nullcontext(), '20220202'),
    ]
)
def test_validate_document_date(
    value: str,
    exception_handler: ContextManager,
    expected_value: Optional[str]
) -> None:
    with exception_handler:
        assert validate_document_date(value=value) == expected_value
