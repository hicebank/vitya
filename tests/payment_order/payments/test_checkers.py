from typing import Optional, Tuple, Type

import pytest
from pydantic import ValidationError

from tests.helpers import parametrize_with_dict
from tests.payment_order.testdata import (
    BIC,
    CBC,
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
    CbcValidationEmptyNotAllowed,
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
    OktmoValidationEmptyNotAllowed,
    OktmoValidationFNSEmptyNotAllowed,
    OktmoValidationZerosNotAllowed,
    OperationKindValidationBudgetValueError,
    PayeeAccountValidationBICValueError,
    PayeeAccountValidationFNSValueError,
    PayeeINNValidationFLLenError,
    PayeeINNValidationIPLenError,
    PayeeINNValidationLELenError,
    PayeeINNValidationNonEmptyError,
    PayeeKPPValidationEmptyNotAllowed,
    PayeeKPPValidationOnlyEmptyError,
    PayerINNValidationEmptyNotAllowedError,
    PayerKPPValidationINN10EmptyNotAllowed,
    PayerKPPValidationINN12OnlyEmptyError,
    PayerStatusValidationCustoms05NotAllowedError,
    PayerStatusValidationNullNotAllowedError,
    PurposeValidationIPNDSError,
    ReasonValidationFNSOnlyEmptyError,
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
    AccountNumber,
    Cbc,
    DocumentDate,
    DocumentNumber,
    OperationKind,
    PayerStatus,
    Purpose,
    Reason,
    TaxPeriod,
    Uin,
)
from vitya.payment_order.payments.checkers import (
    AccountBicChecker,
    BaseModelChecker,
    CbcChecker,
    DocumentDateChecker,
    DocumentNumberChecker,
    OktmoChecker,
    OperationKindChecker,
    PayeeAccountChecker,
    PayeeInnChecker,
    PayeeKppChecker,
    PayerInnChecker,
    PayerKppChecker,
    PayerStatusChecker,
    PurposeChecker,
    ReasonChecker,
    TaxPeriodChecker,
    UinChecker,
)
from vitya.payment_order.payments.helpers import FNS_PAYEE_ACCOUNT_NUMBER
from vitya.pydantic_fields import Bic, Inn, Kpp, Oktmo


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
    else:
        if exception:  # pragma: no cover
            raise NotImplementedError


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
    else:
        if exception:  # pragma: no cover
            raise NotImplementedError


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
    else:
        if exception:  # pragma: no cover
            raise NotImplementedError


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
        (None, '30', False, PaymentType.FNS, PayerINNValidationEmptyNotAllowedError)
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
    else:
        if exception:  # pragma: no cover
            raise NotImplementedError


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
    else:
        if exception:  # pragma: no cover
            raise NotImplementedError


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
    else:
        if exception:  # pragma: no cover
            raise NotImplementedError


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
    else:
        if exceptions:  # pragma: no cover
            raise NotImplementedError


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
    else:
        if exception:  # pragma: no cover
            raise NotImplementedError


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
    else:
        if exception:  # pragma: no cover
            raise NotImplementedError


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
    payer_kpp: Kpp,
    payment_type: PaymentType,
    payer_inn: Inn,
    exception: Type[Exception]
) -> None:
    try:
        TestPayerKppChecker(payer_kpp=payer_kpp, payment_type=payment_type, payer_inn=payer_inn)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        if exception:  # pragma: no cover
            raise NotImplementedError


class TestPayeeKppChecker(BaseModelChecker):
    payee_kpp: Optional[Kpp]
    payment_type: PaymentType

    __checkers__ = [
        (PayeeKppChecker, ['payee_kpp', 'payment_type']),
    ]


@pytest.mark.parametrize(
    'payee_kpp, payment_type, exception',
    [
        (None, PaymentType.FL, None),
        (KPP, PaymentType.FL, PayeeKPPValidationOnlyEmptyError),

        (None, PaymentType.CUSTOMS, PayeeKPPValidationEmptyNotAllowed),
        (KPP, PaymentType.CUSTOMS, None),
    ]
)
def test_payee_kpp_checker(
    payee_kpp: Kpp,
    payment_type: PaymentType,
    exception: Type[Exception]
) -> None:
    try:
        TestPayeeKppChecker(payee_kpp=payee_kpp, payment_type=payment_type)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        if exception:  # pragma: no cover
            raise NotImplementedError


class TestCbcChecker(BaseModelChecker):
    cbc: Optional[Cbc]
    payment_type: PaymentType

    __checkers__ = [
        (CbcChecker, ['cbc', 'payment_type']),
    ]


@pytest.mark.parametrize(
    'cbc, payment_type, exception',
    [
        (None, PaymentType.FL, None),
        (None, PaymentType.FNS, CbcValidationEmptyNotAllowed),
        (None, PaymentType.CUSTOMS, CbcValidationEmptyNotAllowed),
        (CBC, PaymentType.CUSTOMS, None),
    ]
)
def test_cbc_checker(
    cbc: Cbc,
    payment_type: PaymentType,
    exception: Type[Exception]
) -> None:
    try:
        TestCbcChecker(cbc=cbc, payment_type=payment_type)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        if exception:  # pragma: no cover
            raise NotImplementedError


class TestOktmoChecker(BaseModelChecker):
    oktmo: Optional[Oktmo]
    payment_type: PaymentType
    payer_status: PayerStatus

    __checkers__ = [
        (OktmoChecker, ['oktmo', 'payment_type', 'payer_status']),
    ]


@pytest.mark.parametrize(
    'oktmo, payment_type, payer_status, exception',
    [
        (None, PaymentType.FNS, '02', OktmoValidationFNSEmptyNotAllowed),
        (None, PaymentType.FNS, '06', OktmoValidationEmptyNotAllowed),
        ('0' * 8, PaymentType.FNS, '06', OktmoValidationZerosNotAllowed)
    ]
)
def test_oktmo_checker(
    oktmo: Cbc,
    payment_type: PaymentType,
    payer_status: PayerStatus,
    exception: Type[Exception]
) -> None:
    try:
        TestOktmoChecker(oktmo=oktmo, payment_type=payment_type, payer_status=payer_status)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        if exception:  # pragma: no cover
            raise NotImplementedError


class TestReasonChecker(BaseModelChecker):
    reason: Optional[Reason]
    payment_type: PaymentType

    __checkers__ = [
        (ReasonChecker, ['reason', 'payment_type']),
    ]


@pytest.mark.parametrize(
    'reason, payment_type, exception',
    [
        ('ПК', PaymentType.FNS, ReasonValidationFNSOnlyEmptyError),
    ]
)
def test_reason_checker(
    reason: Cbc,
    payment_type: PaymentType,
    exception: Type[Exception]
) -> None:
    try:
        TestReasonChecker(reason=reason, payment_type=payment_type)
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        if exception:  # pragma: no cover
            raise NotImplementedError


class TestTaxPeriodChecker(BaseModelChecker):
    tax_period: Optional[TaxPeriod]
    payment_type: PaymentType
    payer_status: PayerStatus

    __checkers__ = [
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
        ('1' * 9, PaymentType.FNS, '30', TaxPeriodValidationFNSValueLenError),
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
        if exception:  # pragma: no cover
            raise NotImplementedError


class DocumentNumberCheckerChecker(BaseModelChecker):
    document_number: Optional[DocumentNumber]
    payment_type: PaymentType
    reason: Optional[Reason]
    payer_status: PayerStatus
    payee_account: AccountNumber
    uin: Optional[Uin]
    payer_inn: Optional[Inn]

    __checkers__ = [
        (
            DocumentNumberChecker, [
                'document_number', 'payment_type', 'reason',
                'payer_status', 'payee_account', 'uin', 'payer_inn',
            ]
        ),
    ]


@parametrize_with_dict(
    [
        'document_number', 'payment_type', 'payer_status', 'payee_account',
        'payer_inn', 'uin', 'reason', 'exception',
    ],
    [
        {
            'document_number': '02;1222',
            'payment_type': PaymentType.FNS,
            'payer_status': '13',
            'payee_account': IP_ACCOUNT,
            'payer_inn': INN,
            'uin': None,
            'reason': None,
            'exception': DocumentNumberValidationFNSOnlyEmptyError,
        },
        {
            'document_number': '02;1222',
            'payment_type': PaymentType.BUDGET_OTHER,
            'payer_status': '31',
            'payee_account': '03212' + '1' * 15,
            'payer_inn': INN,
            'uin': VALID_UIN,
            'reason': '',
            'exception': DocumentNumberValidationBOOnlyEmptyError,
        },
        {
            'document_number': None,
            'payment_type': PaymentType.BUDGET_OTHER,
            'payer_status': '24',
            'payee_account': IP_ACCOUNT,
            'payer_inn': None,
            'uin': None,
            'reason': '',
            'exception': DocumentNumberValidationBOEmptyNotAllowed,
        },
        {
            'document_number': '1' * 16,
            'payment_type': PaymentType.BUDGET_OTHER,
            'payer_status': '24',
            'payee_account': IP_ACCOUNT,
            'payer_inn': INN,
            'uin': None,
            'reason': '',
            'exception': DocumentNumberValidationBOValueLenError,
        },
        {
            'document_number': '18;',
            'payment_type': PaymentType.BUDGET_OTHER,
            'payer_status': '24',
            'payee_account': IP_ACCOUNT,
            'payer_inn': INN,
            'uin': None,
            'reason': '',
            'exception': DocumentNumberValidationBOValueError,
        },
        {
            'document_number': None,
            'payment_type': PaymentType.CUSTOMS,
            'payer_status': '24',
            'payee_account': IP_ACCOUNT,
            'payer_inn': INN,
            'uin': None,
            'reason': '00',
            'exception': DocumentNumberValidationCustoms00ValueError,
        },
        {
            'document_number': '1' * 8,
            'payment_type': PaymentType.CUSTOMS,
            'payer_status': '24',
            'payee_account': IP_ACCOUNT,
            'payer_inn': INN,
            'uin': None,
            'reason': 'ПК',
            'exception': DocumentNumberValidationCustomsValueLen7Error,
        },
        {
            'document_number': None,
            'payment_type': PaymentType.CUSTOMS,
            'payer_status': '24',
            'payee_account': IP_ACCOUNT,
            'payer_inn': INN,
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
    payee_account: AccountNumber,
    payer_inn: Inn,
    uin: Uin,
    reason: Reason,
    exception: Type[Exception]
) -> None:
    try:
        DocumentNumberCheckerChecker(
            document_number=document_number,
            payment_type=payment_type,
            payer_status=payer_status,
            payee_account=payee_account,
            payer_inn=payer_inn,
            uin=uin,
            reason=reason,
        )
    except ValidationError as e:
        assert isinstance(e.raw_errors[0].exc.errors[0], exception)
    else:
        if exception:  # pragma: no cover
            raise NotImplementedError


class TestDocumentDateChecker(BaseModelChecker):
    document_date: Optional[DocumentDate]
    payment_type: PaymentType

    __checkers__ = [
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
        if exception:  # pragma: no cover
            raise NotImplementedError
