from typing import Optional, Tuple, Type

import pytest
from pydantic import ValidationError

from tests.payment_order.testdata import (
    BIC,
    INN,
    IP_ACCOUNT,
    IP_INN,
    KPP,
    LE_INN,
    VALID_UIN,
)
from vitya.payment_order.enums import PaymentType
from vitya.payment_order.errors import (
    AccountValidationBICValueError,
    OperationKindValidationBudgetValueError,
    PayeeAccountValidationBICValueError,
    PayeeAccountValidationFNSValueError,
    PayeeINNValidationFLLenError,
    PayeeINNValidationIPLenError,
    PayeeINNValidationLELenError,
    PayeeINNValidationNonEmptyError,
    PayerINNValidationEmptyNotAllowedError,
    PayerKPPValidationINN10EmptyNotAllowed,
    PayerKPPValidationINN12OnlyEmptyError,
    PayerStatusValidationCustoms05NotAllowedError,
    PayerStatusValidationNullNotAllowedError,
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
    PayeeInnChecker,
    PayerInnChecker,
    PayerKppChecker,
    PayerStatusChecker,
    PurposeChecker,
    UinChecker,
)
from vitya.payment_order.payments.helpers import FNS_PAYEE_ACCOUNT_NUMBER
from vitya.pydantic_fields import Bic, Inn, Kpp


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
        (None, '13', False, PaymentType.FNS, PayerINNValidationEmptyNotAllowedError)
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
        (VALID_UIN, INN, '13', PaymentType.IP, None),
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


class TestPayeeInnChecker(BaseModelChecker):
    payee_inn: Optional[Inn]
    payment_type: PaymentType

    __checkers__ = [
        (PayeeInnChecker, ['payee_inn', 'payment_type']),
    ]


@pytest.mark.parametrize(
    'payee_inn, payment_type, exception',
    [
        (LE_INN, PaymentType.IP, PayeeINNValidationIPLenError),
        (None, PaymentType.IP, PayeeINNValidationIPLenError),
        (LE_INN, PaymentType.FL, PayeeINNValidationFLLenError),
        (None, PaymentType.CUSTOMS, PayeeINNValidationNonEmptyError),
        (IP_INN, PaymentType.CUSTOMS, PayeeINNValidationLELenError),
    ]
)
def test_payee_inn_checker(
    payee_inn: Inn,
    payment_type: PaymentType,
    exception: Type[Exception]
) -> None:
    try:
        TestPayeeInnChecker(payee_inn=payee_inn, payment_type=payment_type)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)


class TestPayerStatusChecker(BaseModelChecker):
    payer_status: Optional[PayerStatus]
    payment_type: PaymentType
    for_third_face: bool

    __checkers__ = [
        (PayerStatusChecker, ['payer_status', 'payment_type', 'for_third_face']),
    ]


@pytest.mark.parametrize(
    'payer_status, payment_type, for_third_face, exception',
    [
        (None, PaymentType.CUSTOMS, False, PayerStatusValidationNullNotAllowedError),
        ('06', PaymentType.CUSTOMS, True, PayerStatusValidationCustoms05NotAllowedError),
    ]
)
def test_payer_status_checker(
    payer_status: PayerStatus,
    payment_type: PaymentType,
    for_third_face: bool,
    exception: Type[Exception]
) -> None:
    try:
        TestPayerStatusChecker(payer_status=payer_status, payment_type=payment_type, for_third_face=for_third_face)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)


class TestPayerKppChecker(BaseModelChecker):
    payer_kpp: Optional[Kpp]
    payment_type: PaymentType
    payer_inn: Inn

    __checkers__ = [
        (PayerKppChecker, ['payer_kpp', 'payment_type', 'payer_inn']),
    ]


@pytest.mark.parametrize(
    'payer_kpp, payment_type, payer_inn, exception',
    [
        (KPP, PaymentType.FL, INN, None),
        (None, PaymentType.CUSTOMS, LE_INN, PayerKPPValidationINN10EmptyNotAllowed),
        (KPP, PaymentType.CUSTOMS, IP_INN, PayerKPPValidationINN12OnlyEmptyError),
        (KPP, PaymentType.CUSTOMS, LE_INN, None),
    ]
)
def test_payer_kpp_checker(
    payer_kpp: PayerStatus,
    payment_type: PaymentType,
    payer_inn: Inn,
    exception: Type[Exception]
) -> None:
    try:
        TestPayerKppChecker(payer_kpp=payer_kpp, payment_type=payment_type, payer_inn=payer_inn)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
