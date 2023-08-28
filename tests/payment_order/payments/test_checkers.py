from typing import Optional, Tuple, Type
from datetime import datetime

import pytest
from pydantic import ValidationError
from freezegun import freeze_time

from tests.helpers import parametrize_with_dict
from tests.payment_order.testdata import (
    IP_ACCOUNT,
    IP_INN,
    LE_INN,
    VALID_BIC,
    VALID_CBC,
    VALID_INN,
    VALID_KPP,
    VALID_UIN,
)
from vitya.payment_order.enums import PaymentType
from vitya.payment_order.errors import (
    AccountValidationBICValueError,
    CBCValidationEmptyNotAllowed,
    DocumentDateValidationBOLenError,
    DocumentDateValidationCustomsLenError,
    DocumentDateValidationFNSOnlyEmptyError,
    DocumentNumberValidationBOEmptyNotAllowed,
    DocumentNumberValidationBOOnlyEmptyError,
    DocumentNumberValidationBOValueError,
    DocumentNumberValidationBOValueLenError,
    DocumentNumberValidationCustoms00ValueError,
    DocumentNumberValidationCustomsValueLen7Error,
    DocumentNumberValidationCustomsValueLen15Error,
    DocumentNumberValidationFNSOnlyEmptyError,
    OKTMOValidationEmptyNotAllowed,
    OKTMOValidationFNSEmptyNotAllowed,
    OKTMOValidationZerosNotAllowed,
    OperationKindValidationBudgetValueError,
    PayerINNValidationEmptyNotAllowedError,
    PayerKPPValidationINN10EmptyNotAllowed,
    PayerKPPValidationINN12OnlyEmptyError,
    PayerStatusValidationCustoms05NotAllowedError,
    PayerStatusValidationNullNotAllowedError,
    PurposeValidationIPNDSError,
    ReasonValidationValueErrorCustoms,
    ReceiverAccountValidationBICValueError,
    ReceiverAccountValidationFNSValueError,
    ReceiverINNValidationFLLenError,
    ReceiverINNValidationIPLenError,
    ReceiverINNValidationLELenError,
    ReceiverINNValidationNonEmptyError,
    ReceiverKPPValidationEmptyNotAllowed,
    ReceiverKPPValidationOnlyEmptyError,
    TaxPeriodValidationBOValueLenError,
    TaxPeriodValidationCustomsEmptyNotAllowed,
    TaxPeriodValidationCustomsValueLenError,
    TaxPeriodValidationFNS01OnlyEmpty,
    TaxPeriodValidationFNS02EmptyNotAllowed,
    TaxPeriodValidationFNSEmptyNotAllowed,
    TaxPeriodValidationFNSValueLenError,
    UINValidationValueZeroError,
)
from vitya.payment_order.fields import (
    CBC,
    UIN,
    AccountNumber,
    DocumentDate,
    DocumentNumber,
    OperationKind,
    PayerStatus,
    Purpose,
    Reason,
    TaxPeriod,
)
from vitya.payment_order.payments.checkers import (
    BaseModelChecker,
    CBCChecker,
    DocumentDateChecker,
    DocumentNumberChecker,
    OKTMOChecker,
    OperationKindChecker,
    PayerINNChecker,
    PayerKPPChecker,
    PayerStatusChecker,
    PurposeChecker,
    ReasonChecker,
    ReceiverAccountChecker,
    ReceiverINNChecker,
    ReceiverKPPChecker,
    TaxPeriodChecker,
    UINChecker,
)
from vitya.payment_order.payments.constants import FNS_RECEIVER_ACCOUNT_NUMBER, FTS_KPP, CHANGE_YEAR
from vitya.pydantic_fields import BIC, INN, KPP, OKTMO


class TestReceiverAccountModelChecker(BaseModelChecker):
    account_number: AccountNumber
    bic: BIC
    payment_type: PaymentType

    __extra_wired_checkers__ = [
        (ReceiverAccountChecker, ['account_number', 'bic', 'payment_type'])
    ]


@pytest.mark.parametrize(
    'account_number, bic, payment_type, exception',
    [
        (IP_ACCOUNT, VALID_BIC, PaymentType.IP, None),
        (IP_ACCOUNT, VALID_BIC, PaymentType.FNS, ReceiverAccountValidationFNSValueError),
        (FNS_RECEIVER_ACCOUNT_NUMBER, VALID_BIC, PaymentType.FNS, None),
        (IP_ACCOUNT, VALID_BIC[:-1] + '1', PaymentType.IP, ReceiverAccountValidationBICValueError),
    ]
)
def test_receiver_account_checker(
    account_number: AccountNumber,
    bic: BIC,
    payment_type: PaymentType,
    exception: Type[Exception]
) -> None:
    try:
        TestReceiverAccountModelChecker(account_number=account_number, bic=bic, payment_type=payment_type)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        assert exception is None


class TestOperationKindChecker(BaseModelChecker):
    operation_kind: OperationKind
    payment_type: PaymentType

    __extra_wired_checkers__ = [
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
    else:
        assert exception is None


class TestPayerInnChecker(BaseModelChecker):
    payer_inn: Optional[INN]
    payer_status: PayerStatus
    for_third_face: bool
    payment_type: PaymentType

    __extra_wired_checkers__ = [
        (PayerINNChecker, ['payer_inn', 'payer_status', 'for_third_face', 'payment_type']),
    ]


@pytest.mark.parametrize(
    'payer_inn, payer_status, for_third_face, payment_type, exception',
    [
        (VALID_INN, '01', False, PaymentType.IP, None),
        (None, '30', False, PaymentType.FNS, PayerINNValidationEmptyNotAllowedError)
    ]
)
def test_payer_inn_checker(
    payer_inn: INN,
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
    else:
        assert exception is None


class TestUinChecker(BaseModelChecker):
    uin: Optional[UIN]
    receiver_account: AccountNumber
    payer_inn: Optional[INN]
    payer_status: PayerStatus
    payment_type: PaymentType

    __extra_wired_checkers__ = [
        (UINChecker, ['uin', 'receiver_account', 'payer_inn', 'payer_status', 'payment_type']),
    ]


@pytest.mark.parametrize(
    'uin, receiver_account, payer_inn, payer_status, payment_type, exception',
    [
        (VALID_UIN, AccountNumber(IP_ACCOUNT), VALID_INN, '13', PaymentType.IP, None),
        (None, AccountNumber(IP_ACCOUNT), VALID_INN, '31', PaymentType.FNS, UINValidationValueZeroError)
    ]
)
def test_uin_checker(
    uin: UIN,
    receiver_account: AccountNumber,
    payer_inn: INN,
    payer_status: PayerStatus,
    payment_type: PaymentType,
    exception: Type[Exception]
) -> None:
    try:
        TestUinChecker(
            uin=uin,
            receiver_account=receiver_account,
            payer_inn=payer_inn,
            payer_status=payer_status,
            payment_type=payment_type
        )
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        assert exception is None


class TestPurposeChecker(BaseModelChecker):
    purpose: Purpose
    payment_type: PaymentType
    payer_account: AccountNumber

    __extra_wired_checkers__ = [
        (PurposeChecker, ['purpose', 'payment_type', 'payer_account']),
    ]


@pytest.mark.parametrize(
    'purpose, payment_type, payer_account, exception',
    [
        ('some', PaymentType.IP, AccountNumber(IP_ACCOUNT), PurposeValidationIPNDSError),
        ('some', PaymentType.BUDGET_OTHER, AccountNumber(IP_ACCOUNT), None),
        ('some НДС', PaymentType.IP, AccountNumber(IP_ACCOUNT), None),
    ]
)
def test_purpose_checker(
    purpose: Purpose,
    payment_type: PaymentType,
    payer_account: AccountNumber,
    exception: Type[Exception]
) -> None:
    try:
        TestPurposeChecker(purpose=purpose, payment_type=payment_type, payer_account=payer_account)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        assert exception is None


class TestSeveralChecker(BaseModelChecker):
    account_number: AccountNumber
    bic: BIC
    payment_type: PaymentType

    __extra_wired_checkers__ = [
        (ReceiverAccountChecker, ['account_number', 'bic', 'payment_type'])
    ]


@pytest.mark.parametrize(
    'account_number, bic, payment_type, exceptions',
    [
        (IP_ACCOUNT, VALID_BIC[:-1] + '1', PaymentType.FNS,
         (AccountValidationBICValueError, ReceiverAccountValidationFNSValueError))
    ]
)
def test_several_checker(
    account_number: AccountNumber,
    bic: BIC,
    payment_type: PaymentType,
    exceptions: Tuple[Type[Exception]]
) -> None:
    try:
        TestSeveralChecker(account_number=account_number, bic=bic, payment_type=payment_type)
    except ValidationError as e:
        errors = [e for e in e.raw_errors[0].exc.errors]
        assert all(isinstance(error, exceptions) for error in errors)
    else:
        if exceptions:  # pragma: no cover
            raise NotImplementedError


class TestReceiverInnChecker(BaseModelChecker):
    receiver_inn: Optional[INN]
    payment_type: PaymentType

    __extra_wired_checkers__ = [
        (ReceiverINNChecker, ['receiver_inn', 'payment_type']),
    ]


@pytest.mark.parametrize(
    'receiver_inn, payment_type, exception',
    [
        (LE_INN, PaymentType.IP, ReceiverINNValidationIPLenError),
        (None, PaymentType.IP, ReceiverINNValidationIPLenError),
        (LE_INN, PaymentType.FL, ReceiverINNValidationFLLenError),
        (None, PaymentType.CUSTOMS, ReceiverINNValidationNonEmptyError),
        (IP_INN, PaymentType.CUSTOMS, ReceiverINNValidationLELenError),
    ]
)
def test_receiver_inn_checker(
    receiver_inn: INN,
    payment_type: PaymentType,
    exception: Type[Exception]
) -> None:
    try:
        TestReceiverInnChecker(receiver_inn=receiver_inn, payment_type=payment_type)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        assert exception is None


class TestPayerStatusChecker(BaseModelChecker):
    payer_status: Optional[PayerStatus]
    payment_type: PaymentType
    for_third_face: bool

    __extra_wired_checkers__ = [
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
    else:
        assert exception is None


class TestPayerKppChecker(BaseModelChecker):
    payer_kpp: Optional[KPP]
    payment_type: PaymentType
    payer_inn: INN

    __extra_wired_checkers__ = [
        (PayerKPPChecker, ['payer_kpp', 'payment_type', 'payer_inn']),
    ]


@pytest.mark.parametrize(
    'payer_kpp, payment_type, payer_inn, exception',
    [
        (VALID_KPP, PaymentType.FL, VALID_INN, None),
        (None, PaymentType.CUSTOMS, LE_INN, PayerKPPValidationINN10EmptyNotAllowed),
        (VALID_KPP, PaymentType.CUSTOMS, IP_INN, PayerKPPValidationINN12OnlyEmptyError),
        (VALID_KPP, PaymentType.CUSTOMS, LE_INN, None),
    ]
)
def test_payer_kpp_checker(
    payer_kpp: KPP,
    payment_type: PaymentType,
    payer_inn: INN,
    exception: Type[Exception]
) -> None:
    try:
        TestPayerKppChecker(payer_kpp=payer_kpp, payment_type=payment_type, payer_inn=payer_inn)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        assert exception is None


class TestReceiverKppChecker(BaseModelChecker):
    receiver_kpp: Optional[KPP]
    payment_type: PaymentType

    __extra_wired_checkers__ = [
        (ReceiverKPPChecker, ['receiver_kpp', 'payment_type']),
    ]


@pytest.mark.parametrize(
    'receiver_kpp, payment_type, exception',
    [
        (None, PaymentType.FL, None),
        (VALID_KPP, PaymentType.FL, ReceiverKPPValidationOnlyEmptyError),

        (None, PaymentType.CUSTOMS, ReceiverKPPValidationEmptyNotAllowed),
        (FTS_KPP, PaymentType.CUSTOMS, None),
    ]
)
def test_receiver_kpp_checker(
    receiver_kpp: KPP,
    payment_type: PaymentType,
    exception: Type[Exception]
) -> None:
    try:
        TestReceiverKppChecker(receiver_kpp=receiver_kpp, payment_type=payment_type)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        assert exception is None


class TestCBCChecker(BaseModelChecker):
    cbc: Optional[CBC]
    payment_type: PaymentType

    __extra_wired_checkers__ = [
        (CBCChecker, ['cbc', 'payment_type']),
    ]


@pytest.mark.parametrize(
    'cbc, payment_type, exception',
    [
        (None, PaymentType.FL, None),
        (None, PaymentType.FNS, CBCValidationEmptyNotAllowed),
        (None, PaymentType.CUSTOMS, CBCValidationEmptyNotAllowed),
        (VALID_CBC, PaymentType.CUSTOMS, None),
    ]
)
def test_cbc_checker(
    cbc: CBC,
    payment_type: PaymentType,
    exception: Type[Exception]
) -> None:
    try:
        TestCBCChecker(cbc=cbc, payment_type=payment_type)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        assert exception is None


class TestOktmoChecker(BaseModelChecker):
    oktmo: Optional[OKTMO]
    payment_type: PaymentType
    payer_status: PayerStatus

    __extra_wired_checkers__ = [
        (OKTMOChecker, ['oktmo', 'payment_type', 'payer_status']),
    ]


@pytest.mark.parametrize(
    'oktmo, payment_type, payer_status, exception',
    [
        (None, PaymentType.FNS, '02', OKTMOValidationFNSEmptyNotAllowed),
        (None, PaymentType.FNS, '06', OKTMOValidationEmptyNotAllowed),
        ('0' * 8, PaymentType.FNS, '06', OKTMOValidationZerosNotAllowed)
    ]
)
def test_oktmo_checker(
    oktmo: CBC,
    payment_type: PaymentType,
    payer_status: PayerStatus,
    exception: Type[Exception]
) -> None:
    try:
        TestOktmoChecker(oktmo=oktmo, payment_type=payment_type, payer_status=payer_status)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        assert exception is None


class TestReasonChecker(BaseModelChecker):
    reason: Optional[Reason]
    payment_type: PaymentType

    __extra_wired_checkers__ = [
        (ReasonChecker, ['reason', 'payment_type']),
    ]


@pytest.mark.parametrize(
    'reason, payment_type, exception',
    [
        ('ЦЦ', PaymentType.CUSTOMS, ReasonValidationValueErrorCustoms),
    ]
)
def test_reason_checker(
    reason: CBC,
    payment_type: PaymentType,
    exception: Type[Exception]
) -> None:
    try:
        TestReasonChecker(reason=reason, payment_type=payment_type)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        assert exception is None


class TestTaxPeriodChecker(BaseModelChecker):
    tax_period: Optional[TaxPeriod]
    payment_type: PaymentType
    payer_status: PayerStatus

    __extra_wired_checkers__ = [
        (TaxPeriodChecker, ['tax_period', 'payment_type', 'payer_status']),
    ]


@pytest.mark.parametrize(
    'tax_period, payment_type, payer_status, exception',
    [
        ('2' * 11, PaymentType.BUDGET_OTHER, '01', TaxPeriodValidationBOValueLenError),
        (None, PaymentType.CUSTOMS, '01', TaxPeriodValidationCustomsEmptyNotAllowed),
        ('2022022', PaymentType.CUSTOMS, '01', TaxPeriodValidationCustomsValueLenError),
        (None, PaymentType.FNS, '02', TaxPeriodValidationFNS02EmptyNotAllowed),
        ('1', PaymentType.FNS, '01', TaxPeriodValidationFNS01OnlyEmpty),
        ('1', PaymentType.FNS, '13', TaxPeriodValidationFNS01OnlyEmpty),
        (None, PaymentType.FNS, '30', TaxPeriodValidationFNSEmptyNotAllowed),
        ('1' * 9, PaymentType.FNS, '02', TaxPeriodValidationFNSValueLenError),
    ]
)
def test_tax_period_checker(
    tax_period: TaxPeriod,
    payment_type: PaymentType,
    payer_status: PayerStatus,
    exception: Type[Exception]
) -> None:
    try:
        TestTaxPeriodChecker(tax_period=tax_period, payment_type=payment_type, payer_status=payer_status)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        assert exception is None


class DocumentNumberCheckerChecker(BaseModelChecker):
    document_number: Optional[DocumentNumber]
    payment_type: PaymentType
    reason: Optional[Reason]
    payer_status: PayerStatus
    receiver_account: AccountNumber
    uin: Optional[UIN]
    payer_inn: Optional[INN]

    __extra_wired_checkers__ = [
        (
            DocumentNumberChecker, [
                'document_number', 'payment_type', 'reason',
                'payer_status', 'receiver_account', 'uin', 'payer_inn',
            ]
        ),
    ]


@parametrize_with_dict(
    [
        'document_number', 'payment_type', 'payer_status', 'receiver_account',
        'payer_inn', 'uin', 'reason', 'exception',
    ],
    [
        {
            'document_number': '02;1222',
            'payment_type': PaymentType.FNS,
            'payer_status': '13',
            'receiver_account': IP_ACCOUNT,
            'payer_inn': VALID_INN,
            'uin': None,
            'reason': None,
            'exception': DocumentNumberValidationFNSOnlyEmptyError,
        },
        {
            'document_number': '02;1222',
            'payment_type': PaymentType.BUDGET_OTHER,
            'payer_status': '31',
            'receiver_account': '03212' + '1' * 15,
            'payer_inn': VALID_INN,
            'uin': VALID_UIN,
            'reason': '',
            'exception': DocumentNumberValidationBOOnlyEmptyError,
        },
        {
            'document_number': None,
            'payment_type': PaymentType.BUDGET_OTHER,
            'payer_status': '24',
            'receiver_account': IP_ACCOUNT,
            'payer_inn': None,
            'uin': None,
            'reason': '',
            'exception': DocumentNumberValidationBOEmptyNotAllowed,
        },
        {
            'document_number': '1' * 16,
            'payment_type': PaymentType.BUDGET_OTHER,
            'payer_status': '24',
            'receiver_account': IP_ACCOUNT,
            'payer_inn': VALID_INN,
            'uin': None,
            'reason': '',
            'exception': DocumentNumberValidationBOValueLenError,
        },
        {
            'document_number': '18;',
            'payment_type': PaymentType.BUDGET_OTHER,
            'payer_status': '24',
            'receiver_account': IP_ACCOUNT,
            'payer_inn': VALID_INN,
            'uin': None,
            'reason': '',
            'exception': DocumentNumberValidationBOValueError,
        },
        {
            'document_number': None,
            'payment_type': PaymentType.CUSTOMS,
            'payer_status': '24',
            'receiver_account': IP_ACCOUNT,
            'payer_inn': VALID_INN,
            'uin': None,
            'reason': '00',
            'exception': DocumentNumberValidationCustoms00ValueError,
        },
        {
            'document_number': '1' * 8,
            'payment_type': PaymentType.CUSTOMS,
            'payer_status': '24',
            'receiver_account': IP_ACCOUNT,
            'payer_inn': VALID_INN,
            'uin': None,
            'reason': 'ПК',
            'exception': DocumentNumberValidationCustomsValueLen7Error,
        },
        {
            'document_number': None,
            'payment_type': PaymentType.CUSTOMS,
            'payer_status': '24',
            'receiver_account': IP_ACCOUNT,
            'payer_inn': VALID_INN,
            'uin': None,
            'reason': 'ИЛ',
            'exception': DocumentNumberValidationCustomsValueLen15Error,
        },

    ]
)
def test_document_number_checker(
    document_number: DocumentNumber,
    payment_type: PaymentType,
    payer_status: PayerStatus,
    receiver_account: AccountNumber,
    payer_inn: INN,
    uin: UIN,
    reason: Reason,
    exception: Type[Exception]
) -> None:
    try:
        DocumentNumberCheckerChecker(
            document_number=document_number,
            payment_type=payment_type,
            payer_status=payer_status,
            receiver_account=receiver_account,
            payer_inn=payer_inn,
            uin=uin,
            reason=reason,
        )
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        assert exception is None


class TestDocumentDateChecker(BaseModelChecker):
    document_date: Optional[DocumentDate]
    payment_type: PaymentType

    __extra_wired_checkers__ = [
        (DocumentDateChecker, ['document_date', 'payment_type']),
    ]


@pytest.mark.parametrize(
    'document_date, payment_type, exception',
    [
        ('1', PaymentType.FNS, DocumentDateValidationFNSOnlyEmptyError),
        ('1' * 11, PaymentType.CUSTOMS, DocumentDateValidationCustomsLenError),
        ('1' * 11, PaymentType.BUDGET_OTHER, DocumentDateValidationBOLenError),
    ]
)
def test_document_date_checker(
    document_date: DocumentDate,
    payment_type: PaymentType,
    exception: Type[Exception]
) -> None:
    try:
        TestDocumentDateChecker(document_date=document_date, payment_type=payment_type)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        assert exception is None
