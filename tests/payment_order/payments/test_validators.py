from contextlib import nullcontext
from typing import ContextManager, Optional, Type

import pytest

from tests.helpers import parametrize_with_dict
from tests.payment_order.testdata import (
    BIC,
    CBC,
    FL_INN,
    INN,
    IP_ACCOUNT,
    IP_INN,
    KPP,
    LE_INN,
    OKTMO,
    VALID_UIN,
)
from vitya.payment_order.enums import PaymentType
from vitya.payment_order.errors import (
    AccountValidationBICValueError,
    CbcValidationEmptyNotAllowed,
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
    PayerINNValidationCustomsLen10Error,
    PayerINNValidationCustomsLen12Error,
    PayerINNValidationEmptyNotAllowedError,
    PayerINNValidationStartWithZerosError,
    PayerKPPValidationINN10EmptyNotAllowed,
    PayerKPPValidationINN12OnlyEmptyError,
    PayerStatusValidationCustoms05NotAllowedError,
    PayerStatusValidationNullNotAllowedError,
    PurposeCodeValidationFlError,
    PurposeCodeValidationNullError,
    PurposeValidationIPNDSError,
    ReasonValidationFNSOnlyEmptyError,
    TaxPeriodValidationBOValueLenError,
    TaxPeriodValidationCustomsEmptyNotAllowed,
    TaxPeriodValidationCustomsValueLenError,
    TaxPeriodValidationFNS01OnlyEmpty,
    TaxPeriodValidationFNS02EmptyNotAllowed,
    TaxPeriodValidationFNSEmptyNotAllowed,
    TaxPeriodValidationFNSValueLenError,
    UINValidationFNSNotValueZeroError,
    UINValidationFNSValueZeroError,
    UINValidationValueZeroError,
)
from vitya.payment_order.fields import (
    AccountNumber,
    Cbc,
    DocumentNumber,
    OperationKind,
    PayerStatus,
    Reason,
    TaxPeriod,
    Uin,
)
from vitya.payment_order.payments.helpers import FNS_PAYEE_ACCOUNT_NUMBER
from vitya.payment_order.payments.validators import (
    validate_account_by_bic,
    validate_cbc,
    validate_document_number,
    validate_oktmo,
    validate_operation_kind,
    validate_payee_account,
    validate_payee_inn,
    validate_payee_kpp,
    validate_payer_inn,
    validate_payer_kpp,
    validate_payer_status,
    validate_purpose,
    validate_purpose_code,
    validate_reason,
    validate_tax_period,
    validate_uin,
)
from vitya.pydantic_fields import Bic, Inn, Kpp, Oktmo


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
            pytest.raises(PayerINNValidationCustomsLen10Error),
            None,
        ),
        (
            '12345',
            PaymentType.CUSTOMS,
            '16',
            False,
            pytest.raises(PayerINNValidationCustomsLen12Error),
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


@pytest.mark.parametrize(
    'value, payment_type, exception_handler, expected_value',
    [
        (IP_INN, PaymentType.IP, nullcontext(), IP_INN),
        (LE_INN, PaymentType.IP, pytest.raises(PayeeINNValidationIPLenError), None),
        (None, PaymentType.IP, pytest.raises(PayeeINNValidationIPLenError), None),

        (None, PaymentType.FL, nullcontext(), None),
        (FL_INN, PaymentType.FL, nullcontext(), FL_INN),
        (LE_INN, PaymentType.FL, pytest.raises(PayeeINNValidationFLLenError), None),

        (None, PaymentType.CUSTOMS, pytest.raises(PayeeINNValidationNonEmptyError), None),
        (IP_INN, PaymentType.CUSTOMS, pytest.raises(PayeeINNValidationLELenError), None),
        (LE_INN, PaymentType.CUSTOMS, nullcontext(), LE_INN),
    ]
)
def test_validate_payee_inn(
    value: Optional[str],
    payment_type: PaymentType,
    exception_handler: ContextManager,
    expected_value: str
) -> None:
    with exception_handler:
        assert expected_value == validate_payee_inn(value=value, payment_type=payment_type)


@pytest.mark.parametrize(
    'value, payment_type, for_third_face, exception_handler, expected_value',
    [
        ('01', PaymentType.FL, False, nullcontext(), None),
        (None, PaymentType.FL, False, nullcontext(), None),

        (None, PaymentType.CUSTOMS, False, pytest.raises(PayerStatusValidationNullNotAllowedError), None),
        ('06', PaymentType.CUSTOMS, True, pytest.raises(PayerStatusValidationCustoms05NotAllowedError), None),
        ('06', PaymentType.CUSTOMS, False, nullcontext(), '06'),
        ('31', PaymentType.CUSTOMS, True, nullcontext(), '31')
    ]
)
def test_validate_payer_status(
    value: Optional[PayerStatus],
    payment_type: PaymentType,
    for_third_face: bool,
    exception_handler: ContextManager,
    expected_value: Optional[PayerStatus],
) -> None:
    with exception_handler:
        assert expected_value == validate_payer_status(
            value=value,
            payment_type=payment_type,
            for_third_face=for_third_face,
        )


@pytest.mark.parametrize(
    'value, payment_type, payer_inn, exception_handler, expected_value',
    [
        (KPP, PaymentType.FL, INN, nullcontext(), None),
        (None, PaymentType.FL, INN, nullcontext(), None),

        (None, PaymentType.CUSTOMS, LE_INN, pytest.raises(PayerKPPValidationINN10EmptyNotAllowed), None),
        (KPP, PaymentType.CUSTOMS, IP_INN, pytest.raises(PayerKPPValidationINN12OnlyEmptyError), None),

        (KPP, PaymentType.CUSTOMS, LE_INN, nullcontext(), KPP),
    ]
)
def test_validate_payer_kpp(
    value: Optional[Kpp],
    payment_type: PaymentType,
    payer_inn: Inn,
    exception_handler: ContextManager,
    expected_value: Optional[Kpp],
) -> None:
    with exception_handler:
        assert expected_value == validate_payer_kpp(
            value=value,
            payment_type=payment_type,
            payer_inn=payer_inn,
        )


@pytest.mark.parametrize(
    'value, payment_type, exception_handler, expected_value',
    [
        (None, PaymentType.FL, nullcontext(), None),
        (KPP, PaymentType.FL, pytest.raises(PayeeKPPValidationOnlyEmptyError), None),

        (None, PaymentType.FNS, pytest.raises(PayeeKPPValidationEmptyNotAllowed), None),
        (KPP, PaymentType.FNS, nullcontext(), KPP),
    ]
)
def test_validate_payee_kpp(
    value: Optional[Kpp],
    payment_type: PaymentType,
    exception_handler: ContextManager,
    expected_value: Optional[Kpp],
) -> None:
    with exception_handler:
        assert expected_value == validate_payee_kpp(
            value=value,
            payment_type=payment_type,
        )


@pytest.mark.parametrize(
    'value, payment_type, exception_handler, expected_value',
    [
        (None, PaymentType.FL, nullcontext(), None),
        (None, PaymentType.BUDGET_OTHER, nullcontext(), None),
        (CBC, PaymentType.BUDGET_OTHER, nullcontext(), CBC),
        (None, PaymentType.FNS, pytest.raises(CbcValidationEmptyNotAllowed), None),
        (None, PaymentType.CUSTOMS, pytest.raises(CbcValidationEmptyNotAllowed), None),
        (CBC, PaymentType.FNS, nullcontext(), CBC),
    ]
)
def test_validate_cbc(
    value: Optional[Cbc],
    payment_type: PaymentType,
    exception_handler: ContextManager,
    expected_value: Optional[Cbc],
) -> None:
    with exception_handler:
        assert expected_value == validate_cbc(
            value=value,
            payment_type=payment_type,
        )


@pytest.mark.parametrize(
    'value, payment_type, payer_status, exception_handler, expected_value',
    [
        (None, PaymentType.FL, '01', nullcontext(), None),
        (None, PaymentType.FNS, '01', nullcontext(), None),
        (None, PaymentType.FNS, '13', nullcontext(), None),
        (None, PaymentType.CUSTOMS, '13', nullcontext(), None),
        (None, PaymentType.BUDGET_OTHER, '13', nullcontext(), None),
        (None, PaymentType.FNS, '02', pytest.raises(OktmoValidationFNSEmptyNotAllowed), None),
        (None, PaymentType.FNS, '06', pytest.raises(OktmoValidationEmptyNotAllowed), None),
        ('0' * 8, PaymentType.FNS, '06', pytest.raises(OktmoValidationZerosNotAllowed), None),
        (OKTMO, PaymentType.FNS, '06', nullcontext(), OKTMO),
    ]
)
def test_validate_oktmo(
    value: Optional[Oktmo],
    payment_type: PaymentType,
    payer_status: PayerStatus,
    exception_handler: ContextManager,
    expected_value: Optional[Oktmo],
) -> None:
    with exception_handler:
        assert expected_value == validate_oktmo(
            value=value,
            payment_type=payment_type,
            payer_status=payer_status,
        )


@pytest.mark.parametrize(
    'value, payment_type, exception_handler, expected_value',
    [
        (None, PaymentType.FL, nullcontext(), None),
        (None, PaymentType.CUSTOMS, nullcontext(), None),
        (None, PaymentType.BUDGET_OTHER, nullcontext(), None),
        ('ПК', PaymentType.FNS, pytest.raises(ReasonValidationFNSOnlyEmptyError), None),
        (None, PaymentType.FNS, nullcontext(), None),
        ('ПК', PaymentType.BUDGET_OTHER, nullcontext(), 'ПК'),
    ]

)
def test_validate_reason(
    value: Optional[Reason],
    payment_type: PaymentType,
    exception_handler: ContextManager,
    expected_value: Optional[Reason],
) -> None:
    with exception_handler:
        assert expected_value == validate_reason(
            value=value,
            payment_type=payment_type,
        )


@pytest.mark.parametrize(
    'value, payment_type, payer_status, exception_handler, expected_value',
    [
        (None, PaymentType.FL, '01', nullcontext(), None),
        (None, PaymentType.BUDGET_OTHER, '01', nullcontext(), None),
        ('20220222', PaymentType.BUDGET_OTHER, '01', nullcontext(), '20220222'),
        ('2' * 11, PaymentType.BUDGET_OTHER, '01', pytest.raises(TaxPeriodValidationBOValueLenError), None),
        (None, PaymentType.CUSTOMS, '01', pytest.raises(TaxPeriodValidationCustomsEmptyNotAllowed), None),
        ('20220222', PaymentType.CUSTOMS, '01', nullcontext(), '20220222'),
        ('2022022', PaymentType.CUSTOMS, '01', pytest.raises(TaxPeriodValidationCustomsValueLenError), None),

        (None, PaymentType.FNS, '02', pytest.raises(TaxPeriodValidationFNS02EmptyNotAllowed), None),
        ('1' * 10, PaymentType.FNS, '02', nullcontext(), '1' * 10),
        ('1', PaymentType.FNS, '01', pytest.raises(TaxPeriodValidationFNS01OnlyEmpty), None),
        ('1', PaymentType.FNS, '13', pytest.raises(TaxPeriodValidationFNS01OnlyEmpty), None),
        (None, PaymentType.FNS, '01', nullcontext(), None),
        (None, PaymentType.FNS, '13', nullcontext(), None),
        (None, PaymentType.FNS, '30', pytest.raises(TaxPeriodValidationFNSEmptyNotAllowed), None),
        ('1' * 9, PaymentType.FNS, '30', pytest.raises(TaxPeriodValidationFNSValueLenError), None),
        ('1' * 10, PaymentType.FNS, '30', nullcontext(), '1' * 10),
    ]
)
def test_validate_tax_period(
    value: Optional[TaxPeriod],
    payment_type: PaymentType,
    payer_status: PayerStatus,
    exception_handler: ContextManager,
    expected_value: Optional[TaxPeriod],
) -> None:
    with exception_handler:
        assert expected_value == validate_tax_period(
            value=value,
            payment_type=payment_type,
            payer_status=payer_status,
        )


@parametrize_with_dict(
    [
        'value', 'payment_type', 'payer_status', 'payee_account',
        'payer_inn', 'uin', 'reason', 'exception_handler', 'expected_value'
    ],
    [
        {
            'case_id': 1,
            'value': None,
            'payment_type': PaymentType.FL,
            'payer_status': '',
            'payee_account': '',
            'payer_inn': '',
            'uin': '',
            'reason': '',
            'exception_handler': nullcontext(),
            'expected_value': None,
        },
        {
            'case_id': 2,
            'value': None,
            'payment_type': PaymentType.FNS,
            'payer_status': '',
            'payee_account': '',
            'payer_inn': '',
            'uin': '',
            'reason': '',
            'exception_handler': nullcontext(),
            'expected_value': None,
        },
        {
            'case_id': 3,
            'value': '02;1222',
            'payment_type': PaymentType.FNS,
            'payer_status': '',
            'payee_account': '',
            'payer_inn': '',
            'uin': '',
            'reason': '',
            'exception_handler': pytest.raises(DocumentNumberValidationFNSOnlyEmptyError),
            'expected_value': None,
        },
        {
            'case_id': 4,
            'value': '02;1222',
            'payment_type': PaymentType.BUDGET_OTHER,
            'payer_status': '31',
            'payee_account': '03212',
            'payer_inn': '',
            'uin': VALID_UIN,
            'reason': '',
            'exception_handler': pytest.raises(DocumentNumberValidationBOOnlyEmptyError),
            'expected_value': None,
        },
        {
            'case_id': 5,
            'value': None,
            'payment_type': PaymentType.BUDGET_OTHER,
            'payer_status': '31',
            'payee_account': '03212',
            'payer_inn': '',
            'uin': VALID_UIN,
            'reason': '',
            'exception_handler': nullcontext(),
            'expected_value': None,
        },
        {
            'case_id': 6,
            'value': None,
            'payment_type': PaymentType.BUDGET_OTHER,
            'payer_status': '24',
            'payee_account': '03212',
            'payer_inn': None,
            'uin': None,
            'reason': '',
            'exception_handler': pytest.raises(DocumentNumberValidationBOEmptyNotAllowed),
            'expected_value': None,
        },
        {
            'case_id': 7,
            'value': None,
            'payment_type': PaymentType.BUDGET_OTHER,
            'payer_status': '24',
            'payee_account': '03212',
            'payer_inn': INN,
            'uin': None,
            'reason': '',
            'exception_handler': nullcontext(),
            'expected_value': None,
        },
        {
            'case_id': 8,
            'value': '1' * 16,
            'payment_type': PaymentType.BUDGET_OTHER,
            'payer_status': '24',
            'payee_account': '03212',
            'payer_inn': INN,
            'uin': None,
            'reason': '',
            'exception_handler': pytest.raises(DocumentNumberValidationBOValueLenError),
            'expected_value': None,
        },
        {
            'case_id': 9,
            'value': '18;',
            'payment_type': PaymentType.BUDGET_OTHER,
            'payer_status': '24',
            'payee_account': '03212',
            'payer_inn': INN,
            'uin': None,
            'reason': '',
            'exception_handler': pytest.raises(DocumentNumberValidationBOValueError),
            'expected_value': None,
        },
        {
            'case_id': 10,
            'value': None,
            'payment_type': PaymentType.CUSTOMS,
            'payer_status': '24',
            'payee_account': '03212',
            'payer_inn': INN,
            'uin': None,
            'reason': '00',
            'exception_handler': pytest.raises(DocumentNumberValidationCustoms00ValueError),
            'expected_value': None,
        },
        {
            'case_id': 11,
            'value': '1' * 8,
            'payment_type': PaymentType.CUSTOMS,
            'payer_status': '24',
            'payee_account': '03212',
            'payer_inn': INN,
            'uin': None,
            'reason': 'ПК',
            'exception_handler': pytest.raises(DocumentNumberValidationCustomsValueLen7Error),
            'expected_value': None,
        },
        {
            'case_id': 11,
            'value': None,
            'payment_type': PaymentType.CUSTOMS,
            'payer_status': '24',
            'payee_account': '03212',
            'payer_inn': INN,
            'uin': None,
            'reason': 'ИЛ',
            'exception_handler': pytest.raises(DocumentNumberValidationCustomsValueLen15Error),
            'expected_value': None,
        },
        {
            'case_id': 12,
            'value': '01',
            'payment_type': PaymentType.CUSTOMS,
            'payer_status': '24',
            'payee_account': '03212',
            'payer_inn': INN,
            'uin': None,
            'reason': 'ИЛ',
            'exception_handler': nullcontext(),
            'expected_value': '01',
        }
    ]
)
def test_validate_document_number(
    value: Optional[DocumentNumber],
    payment_type: PaymentType,
    payer_status: Optional[PayerStatus],
    payee_account: AccountNumber,
    payer_inn: Optional[Inn],
    uin: Optional[Uin],
    reason: Optional[str],
    exception_handler: ContextManager,
    expected_value: Optional[DocumentNumber],
) -> None:
    with exception_handler:
        assert expected_value == validate_document_number(
            value=value,
            payment_type=payment_type,
            payer_status=payer_status,
            payee_account=payee_account,
            payer_inn=payer_inn,
            uin=uin,
            reason=reason,
        )
