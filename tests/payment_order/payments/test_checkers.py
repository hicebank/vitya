from typing import Optional, Tuple, Type

import pytest
from pydantic import ValidationError

from tests.payment_order.testdata import BIC, INN, IP_ACCOUNT, VALID_UIN
from vitya.payment_order.enums import PaymentType
from vitya.payment_order.errors import (
    AccountValidationBICValueError,
    OperationKindValidationBudgetValueError,
    PayeeAccountValidationBICValueError,
    PayeeAccountValidationFNSValueError,
    PayerINNValidationEmptyNotAllowedError,
    PurposeValidationIPNDSError,
    UINValidationValueZeroError,
)
from vitya.payment_order.fields import (
    AccountNumber,
    OperationKind,
    PayerStatus,
    Purpose,
    Uin,
)
from vitya.payment_order.payments.checkers import (
    AccountBicChecker,
    BaseModelChecker,
    OperationKindChecker,
    PayeeAccountChecker,
    PayerInnChecker,
    PurposeChecker,
    UinChecker,
)
from vitya.payment_order.payments.helpers import FNS_PAYEE_ACCOUNT_NUMBER
from vitya.pydantic_fields import Bic, Inn


class TestAccountBicModelChecker(BaseModelChecker):
    account_number: AccountNumber
    bic: Bic

    __checkers__ = [
        (AccountBicChecker, ['account_number', 'bic'])
    ]


@pytest.mark.parametrize(
    'account_number, bic, exception',
    [
        (IP_ACCOUNT, BIC, None),
        (IP_ACCOUNT, BIC[:-1] + '1', AccountValidationBICValueError)
    ]
)
def test_account_bic_checker(
    account_number: AccountNumber,
    bic: Bic,
    exception: Type[Exception]
) -> None:
    try:
        TestAccountBicModelChecker(account_number=account_number, bic=bic)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)


class TestPayeeAccountModelChecker(BaseModelChecker):
    account_number: AccountNumber
    bic: Bic
    payment_type: PaymentType

    __checkers__ = [
        (PayeeAccountChecker, ['account_number', 'bic', 'payment_type'])
    ]


@pytest.mark.parametrize(
    'account_number, bic, payment_type, exception',
    [
        (IP_ACCOUNT, BIC, PaymentType.IP, None),
        (IP_ACCOUNT, BIC, PaymentType.FNS, PayeeAccountValidationFNSValueError),
        (FNS_PAYEE_ACCOUNT_NUMBER, BIC, PaymentType.FNS, None),
        (IP_ACCOUNT, BIC[:-1] + '1', PaymentType.IP, PayeeAccountValidationBICValueError),
    ]
)
def test_payee_account_checker(
    account_number: AccountNumber,
    bic: Bic,
    payment_type: PaymentType,
    exception: Type[Exception]
) -> None:
    try:
        TestPayeeAccountModelChecker(account_number=account_number, bic=bic, payment_type=payment_type)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)


class TestOperationKindChecker(BaseModelChecker):
    operation_kind: OperationKind
    payment_type: PaymentType

    __checkers__ = [
        (OperationKindChecker, ['operation_kind', 'payment_type'])
    ]


@pytest.mark.parametrize(
    'operation_kind, payment_type, exception',
    [
        ('01', PaymentType.FNS, None),
        ('03', PaymentType.FNS, OperationKindValidationBudgetValueError),
        ('03', PaymentType.IP, None),
    ]
)
def test_operation_kind_checker(
    operation_kind: OperationKind,
    payment_type: PaymentType,
    exception: Type[Exception]
) -> None:
    try:
        TestOperationKindChecker(operation_kind=operation_kind, payment_type=payment_type)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)


class TestPayerInnChecker(BaseModelChecker):
    payer_inn: Optional[Inn]
    payer_status: PayerStatus
    for_third_face: bool
    payment_type: PaymentType

    __checkers__ = [
        (PayerInnChecker, ['payer_inn', 'payer_status', 'for_third_face', 'payment_type']),
    ]


@pytest.mark.parametrize(
    'payer_inn, payer_status, for_third_face, payment_type, exception',
    [
        (INN, '01', False, PaymentType.IP, None),
        (None, '11', False, PaymentType.FNS, PayerINNValidationEmptyNotAllowedError)
    ]
)
def test_payer_inn_checker(
    payer_inn: Inn,
    payer_status: PayerStatus,
    for_third_face: bool,
    payment_type: PaymentType,
    exception: Type[Exception]
) -> None:
    try:
        TestPayerInnChecker(
            payer_inn=payer_inn,
            payer_status=payer_status,
            for_third_face=for_third_face,
            payment_type=payment_type
        )
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)


class TestUinChecker(BaseModelChecker):
    uin: Optional[Uin]
    payer_inn: Optional[Inn]
    payer_status: PayerStatus
    payment_type: PaymentType

    __checkers__ = [
        (UinChecker, ['uin', 'payer_inn', 'payer_status', 'payment_type']),
    ]


@pytest.mark.parametrize(
    'uin, payer_inn, payer_status, payment_type, exception',
    [
        (VALID_UIN, INN, '11', PaymentType.IP, None),
        (None, INN, '31', PaymentType.FNS, UINValidationValueZeroError)
    ]
)
def test_uin_checker(
    uin: Uin,
    payer_inn: Inn,
    payer_status: PayerStatus,
    payment_type: PaymentType,
    exception: Type[Exception]
) -> None:
    try:
        TestUinChecker(
            uin=uin,
            payer_inn=payer_inn,
            payer_status=payer_status,
            payment_type=payment_type
        )
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)


class TestPurposeChecker(BaseModelChecker):
    purpose: Purpose
    payment_type: PaymentType

    __checkers__ = [
        (PurposeChecker, ['purpose', 'payment_type']),
    ]


@pytest.mark.parametrize(
    'purpose, payment_type, exception',
    [
        ('some', PaymentType.IP, PurposeValidationIPNDSError),
    ]
)
def test_purpose_checker(
    purpose: Purpose,
    payment_type: PaymentType,
    exception: Type[Exception]
) -> None:
    try:
        TestPurposeChecker(purpose=purpose, payment_type=payment_type)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)


class TestSeveralChecker(BaseModelChecker):
    account_number: AccountNumber
    bic: Bic
    payment_type: PaymentType

    __checkers__ = [
        (AccountBicChecker, ['account_number', 'bic']),
        (PayeeAccountChecker, ['account_number', 'bic', 'payment_type'])
    ]


@pytest.mark.parametrize(
    'account_number, bic, payment_type, exceptions',
    [
        (IP_ACCOUNT, BIC[:-1] + '1', PaymentType.FNS,
         (AccountValidationBICValueError, PayeeAccountValidationFNSValueError))
    ]
)
def test_several_checker(
    account_number: AccountNumber,
    bic: Bic,
    payment_type: PaymentType,
    exceptions: Tuple[Type[Exception]]
) -> None:
    try:
        TestSeveralChecker(account_number=account_number, bic=bic, payment_type=payment_type)
    except ValidationError as e:
        errors = [e for e in e.raw_errors[0].exc.errors]
        assert all(isinstance(error, exceptions) for error in errors)
