from contextlib import nullcontext
from typing import ContextManager, Optional, Type

import pytest

from tests.payment_order.testdata import BIC, INN, IP_ACCOUNT, VALID_UIN
from vitya.payment_order.enums import PaymentType
from vitya.payment_order.errors import (
    AccountValidationBICValueError,
    OperationKindValidationBudgetValueError,
    PayeeAccountValidationBICValueError,
    PayeeAccountValidationFNSValueError,
    PayerINNValidationEmptyNotAllowedError,
    PayerINNValidationStartWithZerosError,
    PayerINNValidationTMSLen10Error,
    PayerINNValidationTMSLen12Error,
    PurposeCodeValidationFlError,
    PurposeCodeValidationNullError,
    PurposeValidationIPNDSError,
    UINValidationFNSNotValueZeroError,
    UINValidationFNSValueZeroError,
    UINValidationValueZeroError,
)
from vitya.payment_order.fields import AccountNumber, OperationKind, PayerStatus
from vitya.payment_order.payments.helpers import FNS_PAYEE_ACCOUNT_NUMBER
from vitya.payment_order.payments.validators import (
    validate_account_by_bic,
    validate_operation_kind,
    validate_payee_account,
    validate_payer_inn,
    validate_purpose,
    validate_purpose_code,
    validate_uin,
)
from vitya.pydantic_fields import Bic


@pytest.mark.parametrize(
    'value, payment_type, payee_bic, exception_handler, expected_value',
    [
        (IP_ACCOUNT, PaymentType.IP, BIC, nullcontext(), IP_ACCOUNT),
        (FNS_PAYEE_ACCOUNT_NUMBER, PaymentType.FNS, '', nullcontext(), FNS_PAYEE_ACCOUNT_NUMBER),
        (FNS_PAYEE_ACCOUNT_NUMBER[:-1], PaymentType.FNS, '', pytest.raises(PayeeAccountValidationFNSValueError), None),
        (IP_ACCOUNT, PaymentType.IP, BIC[:-1] + '1', pytest.raises(PayeeAccountValidationBICValueError), None),
    ]
)
def test_validate_payee_account(
    value: AccountNumber,
    payment_type: PaymentType,
    payee_bic: Bic,
    exception_handler: ContextManager,
    expected_value: str
) -> None:
    with exception_handler:
        assert validate_payee_account(value=value, payment_type=payment_type, payee_bic=payee_bic) == expected_value


@pytest.mark.parametrize(
    'account_number, bic, exception_handler',
    [
        (IP_ACCOUNT, BIC, nullcontext()),
        (IP_ACCOUNT[:-1] + '0', BIC, pytest.raises(AccountValidationBICValueError)),
    ]
)
def test_validate_account_by_bic(
    account_number: AccountNumber,
    bic: Bic,
    exception_handler: ContextManager,
) -> None:
    with exception_handler:
        validate_account_by_bic(account_number=account_number, bic=bic)


@pytest.mark.parametrize(
    'value, payment_type, exception_handler, expected_value',
    [
        ('02', PaymentType.IP, nullcontext(), '02'),
        ('02', PaymentType.BUDGET_OTHER, nullcontext(), '02'),
        ('03', PaymentType.BUDGET_OTHER, pytest.raises(OperationKindValidationBudgetValueError), None),
    ]
)
def test_validate_operation_kind(
    value: OperationKind,
    payment_type: PaymentType,
    exception_handler: ContextManager,
    expected_value: str
) -> None:
    with exception_handler:
        assert validate_operation_kind(value=value, payment_type=payment_type) == expected_value


@pytest.mark.parametrize(
    'value, payment_type, exception_handler, expected_value',
    [
        (1, PaymentType.FL, nullcontext(), 1),
        (6, PaymentType.FL, pytest.raises(PurposeCodeValidationFlError), None),
        (None, PaymentType.IP, nullcontext(), None),
        (1, PaymentType.IP, pytest.raises(PurposeCodeValidationNullError), None),
    ]
)
def test_validate_purpose_code(
    value: int,
    payment_type: PaymentType,
    exception_handler: ContextManager,
    expected_value: int
) -> None:
    with exception_handler:
        assert validate_purpose_code(value=value, payment_type=payment_type) == expected_value


@pytest.mark.parametrize(
    'value, payment_type, payer_status, payer_inn, exception_handler, expected_value',
    [
        (
            '',
            PaymentType.FL,
            '',
            '',
            nullcontext(),
            None,
        ),
        (
            None,
            PaymentType.FL,
            '',
            '',
            nullcontext(),
            None,
        ),
        (
            None,
            PaymentType.FNS,
            '31',
            '',
            pytest.raises(UINValidationValueZeroError),
            None,
        ),
        (
            VALID_UIN,
            PaymentType.BUDGET_OTHER,
            '',
            '',
            nullcontext(),
            VALID_UIN,
        ),
        (
            None,
            PaymentType.FNS,
            '13',
            None,
            pytest.raises(UINValidationFNSValueZeroError),
            None,
        ),
        (
            VALID_UIN,
            PaymentType.FNS,
            '13',
            '',
            nullcontext(),
            VALID_UIN,
        ),
        (
            VALID_UIN,
            PaymentType.FNS,
            '02',
            '',
            pytest.raises(UINValidationFNSNotValueZeroError),
            None,
        ),
        (
            None,
            PaymentType.FNS,
            '02',
            '',
            nullcontext(),
            None,
        ),
    ]
)
def test_validate_uin(
    value: Optional[str],
    payment_type: PaymentType,
    payer_status: PayerStatus,
    payer_inn: str,
    exception_handler: Optional[Type[Exception]],
    expected_value: str
) -> None:
    with exception_handler:
        assert validate_uin(
            value=value,
            payment_type=payment_type,
            payer_inn=payer_inn,
            payer_status=payer_status,
        ) == expected_value


@pytest.mark.parametrize(
    'value, payment_type, exception_handler, expected_value',
    [
        (None, PaymentType.FNS, nullcontext(), None),
        ('some', PaymentType.IP, pytest.raises(PurposeValidationIPNDSError), None),
        ('some with НДС', PaymentType.IP, nullcontext(), 'some with НДС'),
    ]
)
def test_validate_purpose(
    value: Optional[str],
    payment_type: PaymentType,
    exception_handler: ContextManager,
    expected_value: str
) -> None:
    with exception_handler:
        assert validate_purpose(payment_type=payment_type, value=value) == expected_value


@pytest.mark.parametrize(
    'value, payment_type, payer_status, for_third_face, exception_handler, expected_value',
    [
        (
            INN,
            PaymentType.FL,
            '',
            False,
            nullcontext(),
            INN,
        ),
        (
            None,
            PaymentType.BUDGET_OTHER,
            '',
            False,
            nullcontext(),
            None,
        ),
        (
            None,
            PaymentType.FNS,
            '13',
            False,
            nullcontext(),
            None,
        ),
        (
            None,
            PaymentType.CUSTOMS,
            '30',
            False,
            nullcontext(),
            None,
        ),
        (
            None,
            PaymentType.FNS,
            '14',
            False,
            pytest.raises(PayerINNValidationEmptyNotAllowedError),
            None,
        ),
        (
            None,
            PaymentType.CUSTOMS,
            '31',
            False,
            pytest.raises(PayerINNValidationEmptyNotAllowedError),
            None,
        ),
        (
            '12345',
            PaymentType.CUSTOMS,
            '06',
            True,
            pytest.raises(PayerINNValidationTMSLen10Error),
            None,
        ),
        (
            '12345',
            PaymentType.CUSTOMS,
            '16',
            False,
            pytest.raises(PayerINNValidationTMSLen12Error),
            None,
        ),
        (
            '00123',
            PaymentType.CUSTOMS,
            '',
            False,
            pytest.raises(PayerINNValidationStartWithZerosError),
            None,
        ),
        (
            '00000',
            PaymentType.CUSTOMS,
            '',
            False,
            pytest.raises(PayerINNValidationStartWithZerosError),
            None,
        ),
        (
            INN,
            PaymentType.CUSTOMS,
            '',
            False,
            nullcontext(),
            INN,
        ),
    ]
)
def test_validate_payer_inn(
    value: Optional[str],
    payment_type: PaymentType,
    payer_status: PayerStatus,
    for_third_face: bool,
    exception_handler: ContextManager,
    expected_value: str
) -> None:
    with exception_handler:
        assert expected_value == validate_payer_inn(
            value=value, payment_type=payment_type, payer_status=payer_status, for_third_face=for_third_face
        )
