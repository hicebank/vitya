from contextlib import nullcontext
from datetime import datetime
from typing import ContextManager, Optional, Type

import pytest
from freezegun import freeze_time

from tests.helpers import parametrize_with_dict
from tests.payment_order.testdata import (
    FL_INN,
    IP_ACCOUNT,
    IP_INN,
    LE_INN,
    VALID_BIC,
    VALID_CBC,
    VALID_INN,
    VALID_KPP,
    VALID_OKTMO,
    VALID_UIN,
)
from vitya.payment_order.enums import PaymentType
from vitya.payment_order.errors import (
    AccountValidationBICValueError,
    BudgetPaymentForThirdPersonError,
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
    OKTMOValidationFTS,
    OKTMOValidationZerosNotAllowed,
    OperationKindValidationBudgetValueError,
    PayerINNValidationCustomsLen10Error,
    PayerINNValidationCustomsLen12Error,
    PayerINNValidationEmptyNotAllowedError,
    PayerINNValidationStartWithZerosError,
    PayerKPPValidationINN10EmptyNotAllowed,
    PayerKPPValidationINN12OnlyEmptyError,
    PayerStatusValidationCustoms05NotAllowedError,
    PayerStatusValidationNullNotAllowedError,
    PurposeCodeValidationChameleonError,
    PurposeCodeValidationFlError,
    PurposeCodeValidationNullError,
    PurposeValidationIPNDSError,
    ReasonValidationValueErrorCustoms,
    ReasonValidationValueErrorFNS,
    ReceiverAccountValidationBICValueError,
    ReceiverAccountValidationFNSValueError,
    ReceiverINNValidationFLLenError,
    ReceiverINNValidationIPLenError,
    ReceiverINNValidationLELenError,
    ReceiverINNValidationNonEmptyError,
    ReceiverKPPValidationEmptyNotAllowed,
    ReceiverKPPValidationFNS,
    ReceiverKPPValidationFTS,
    ReceiverKPPValidationOnlyEmptyError,
    ReceiverKPPValidationStartsWithZeros,
    TaxPeriodValidationBOValueLenError,
    TaxPeriodValidationCustomsEmptyNotAllowed,
    TaxPeriodValidationCustomsValueLenError,
    TaxPeriodValidationFNS01OnlyEmpty,
    TaxPeriodValidationFNS02EmptyNotAllowed,
    TaxPeriodValidationFNSEmptyNotAllowed,
    TaxPeriodValidationFNSValueLenError,
    UINValidationBONotEmpty,
    UINValidationFNSNotValueZeroError,
    UINValidationFNSValueZeroError,
    UINValidationValueZeroError,
)
from vitya.payment_order.fields import (
    CBC,
    UIN,
    AccountNumber,
    DocumentNumber,
    OperationKind,
    PayerStatus,
    Reason,
    TaxPeriod,
)
from vitya.payment_order.payments.checks import (
    check_account_by_bic,
    check_cbc,
    check_document_date,
    check_document_number,
    check_oktmo,
    check_oktmo_with_payer_status,
    check_operation_kind,
    check_payer_inn,
    check_payer_kpp,
    check_payer_status,
    check_payment_type_and_for_third_person,
    check_purpose,
    check_purpose_code,
    check_reason,
    check_receiver_account,
    check_receiver_inn,
    check_receiver_kpp,
    check_tax_period,
    check_uin,
)
from vitya.payment_order.payments.constants import (
    CHANGE_YEAR,
    FNS_KPP,
    FNS_RECEIVER_ACCOUNT_NUMBER,
    FTS_OKTMO,
)
from vitya.pydantic_fields import BIC, INN, KPP, OKTMO


@pytest.mark.parametrize(
    'value, payment_type, receiver_bic, exception_handler, expected_value',
    [
        (IP_ACCOUNT, PaymentType.IP, VALID_BIC, nullcontext(), IP_ACCOUNT),
        (FNS_RECEIVER_ACCOUNT_NUMBER, PaymentType.FNS, '', nullcontext(), FNS_RECEIVER_ACCOUNT_NUMBER),
        (FNS_RECEIVER_ACCOUNT_NUMBER[:-1], PaymentType.FNS, '', pytest.raises(ReceiverAccountValidationFNSValueError), None),
        (IP_ACCOUNT, PaymentType.IP, VALID_BIC[:-1] + '1', pytest.raises(ReceiverAccountValidationBICValueError), None),
    ]
)
def test_check_receiver_account(
    value: AccountNumber,
    payment_type: PaymentType,
    receiver_bic: BIC,
    exception_handler: ContextManager,
    expected_value: str
) -> None:
    with exception_handler:
        assert check_receiver_account(value=value, payment_type=payment_type, receiver_bic=receiver_bic) == expected_value


@pytest.mark.parametrize(
    'account_number, bic, exception_handler',
    [
        (IP_ACCOUNT, VALID_BIC, nullcontext()),
        (IP_ACCOUNT[:-1] + '0', VALID_BIC, pytest.raises(AccountValidationBICValueError)),
    ]
)
def test_check_account_by_bic(
    account_number: AccountNumber,
    bic: BIC,
    exception_handler: ContextManager,
) -> None:
    with exception_handler:
        check_account_by_bic(account_number=account_number, bic=bic)


@pytest.mark.parametrize(
    'value, payment_type, exception_handler, expected_value',
    [
        ('03', PaymentType.BUDGET_OTHER, pytest.raises(OperationKindValidationBudgetValueError), None),
    ]
)
def test_check_operation_kind(
    value: OperationKind,
    payment_type: PaymentType,
    exception_handler: ContextManager,
    expected_value: str
) -> None:
    with exception_handler:
        assert check_operation_kind(value=value, payment_type=payment_type) == expected_value


@freeze_time(datetime(CHANGE_YEAR - 1, 12, 31))
@pytest.mark.parametrize(
    'value, payment_type, exception_handler, expected_value',
    [
        ('02', PaymentType.IP, nullcontext(), '02'),
        ('02', PaymentType.BUDGET_OTHER, nullcontext(), '02'),
    ]
)
def test_check_operation_kind_before_2024(
    value: OperationKind,
    payment_type: PaymentType,
    exception_handler: ContextManager,
    expected_value: str
) -> None:
    with exception_handler:
        assert check_operation_kind(value=value, payment_type=payment_type) == expected_value


@pytest.mark.parametrize(
    'value, payment_type, exception_handler, expected_value',
    [
        (1, PaymentType.FL, nullcontext(), 1),
        (6, PaymentType.FL, pytest.raises(PurposeCodeValidationFlError), None),
        (6, PaymentType.CHAMELEON, pytest.raises(PurposeCodeValidationChameleonError), None),
        (None, PaymentType.IP, nullcontext(), None),
        (1, PaymentType.IP, pytest.raises(PurposeCodeValidationNullError), None),
    ]
)
def test_check_purpose_code(
    value: int,
    payment_type: PaymentType,
    exception_handler: ContextManager,
    expected_value: int
) -> None:
    with exception_handler:
        assert check_purpose_code(value=value, payment_type=payment_type) == expected_value


@pytest.mark.parametrize(
    'value, payment_type, receiver_account, payer_status, payer_inn, exception_handler, expected_value',
    [
        ('', PaymentType.FL, AccountNumber(IP_ACCOUNT), '', '', nullcontext(), None),
        (None, PaymentType.FL, AccountNumber(IP_ACCOUNT), '', '', nullcontext(), None),
        (None, PaymentType.FNS, AccountNumber(IP_ACCOUNT), '31', '', pytest.raises(UINValidationValueZeroError), None),
        (VALID_UIN, PaymentType.BUDGET_OTHER, AccountNumber(IP_ACCOUNT), '', '', nullcontext(), VALID_UIN),
        (
            None,
            PaymentType.BUDGET_OTHER,
            AccountNumber('03212810722200035222'),
            '',
            '',
            pytest.raises(UINValidationBONotEmpty),
            VALID_UIN,
        ),
        (
            None,
            PaymentType.FNS,
            AccountNumber(IP_ACCOUNT),
            '13',
            None,
            pytest.raises(UINValidationFNSValueZeroError),
            None,
        ),
        (
            VALID_UIN,
            PaymentType.FNS,
            AccountNumber(IP_ACCOUNT),
            '13',
            '',
            nullcontext(),
            VALID_UIN,
        ),
    ]
)
def test_check_uin(
    value: Optional[str],
    receiver_account: AccountNumber,
    payment_type: PaymentType,
    payer_status: PayerStatus,
    payer_inn: str,
    exception_handler: Optional[Type[Exception]],
    expected_value: str
) -> None:
    with exception_handler:
        assert check_uin(
            value=value,
            receiver_account=receiver_account,
            payment_type=payment_type,
            payer_inn=payer_inn,
            payer_status=payer_status,
        ) == expected_value


@freeze_time(datetime(CHANGE_YEAR - 1, 12, 31))
@pytest.mark.parametrize(
    'value, payment_type, receiver_account, payer_status, payer_inn, exception_handler, expected_value',
    [
        (
            VALID_UIN,
            PaymentType.FNS,
            AccountNumber(IP_ACCOUNT),
            '02',
            '',
            pytest.raises(UINValidationFNSNotValueZeroError),
            None,
        ),
        (
            None,
            PaymentType.FNS,
            AccountNumber(IP_ACCOUNT),
            '02',
            '',
            nullcontext(),
            None,
        ),
    ]
)
def test_check_uin_before_2024(
    value: Optional[str],
    receiver_account: AccountNumber,
    payment_type: PaymentType,
    payer_status: PayerStatus,
    payer_inn: str,
    exception_handler: Optional[Type[Exception]],
    expected_value: str
) -> None:
    with exception_handler:
        assert check_uin(
            value=value,
            receiver_account=receiver_account,
            payment_type=payment_type,
            payer_inn=payer_inn,
            payer_status=payer_status,
        ) == expected_value


@pytest.mark.parametrize(
    'value, payment_type, payer_account, exception_handler, expected_value',
    [
        (None, PaymentType.IP, AccountNumber(IP_ACCOUNT), pytest.raises(PurposeValidationIPNDSError), None),
        ('some', PaymentType.IP, AccountNumber(IP_ACCOUNT), pytest.raises(PurposeValidationIPNDSError), None),
        ('some', PaymentType.BUDGET_OTHER, AccountNumber(IP_ACCOUNT), nullcontext(), 'some'),
        ('some with НДС', PaymentType.IP, AccountNumber(IP_ACCOUNT), nullcontext(), 'some with НДС'),
    ]
)
def test_check_purpose(
    value: Optional[str],
    payment_type: PaymentType,
    payer_account: AccountNumber,
    exception_handler: ContextManager,
    expected_value: str
) -> None:
    with exception_handler:
        assert check_purpose(value=value, payment_type=payment_type, payer_account=payer_account) == expected_value


@pytest.mark.parametrize(
    'value, payment_type, payer_status, for_third_person, exception_handler, expected_value',
    [
        (VALID_INN, PaymentType.FL, '', False, nullcontext(), VALID_INN),
        (None, PaymentType.BUDGET_OTHER, '', False, nullcontext(), None),
        (None, PaymentType.FNS, '13', False, nullcontext(), None),
        (None, PaymentType.CUSTOMS, '30', False, nullcontext(), None),
        (None, PaymentType.FNS, '14', False, pytest.raises(PayerINNValidationEmptyNotAllowedError), None),
        (None, PaymentType.CUSTOMS, '31', False, pytest.raises(PayerINNValidationEmptyNotAllowedError), None),
        ('12345', PaymentType.CUSTOMS, '06', True, pytest.raises(PayerINNValidationCustomsLen10Error), None),
        ('12345', PaymentType.CUSTOMS, '16', False, pytest.raises(PayerINNValidationCustomsLen12Error), None),
        ('00123', PaymentType.CUSTOMS, '', False, pytest.raises(PayerINNValidationStartWithZerosError), None),
        ('00000', PaymentType.CUSTOMS, '', False, pytest.raises(PayerINNValidationStartWithZerosError), None),
        (VALID_INN, PaymentType.CUSTOMS, '', False, nullcontext(), VALID_INN),
    ]
)
def test_check_payer_inn(
    value: Optional[str],
    payment_type: PaymentType,
    payer_status: PayerStatus,
    for_third_person: bool,
    exception_handler: ContextManager,
    expected_value: str
) -> None:
    with exception_handler:
        assert expected_value == check_payer_inn(
            value=value, payment_type=payment_type, payer_status=payer_status, for_third_person=for_third_person
        )


@pytest.mark.parametrize(
    'value, payment_type, exception_handler, expected_value',
    [
        (IP_INN, PaymentType.IP, nullcontext(), IP_INN),
        (LE_INN, PaymentType.IP, pytest.raises(ReceiverINNValidationIPLenError), None),
        (None, PaymentType.IP, pytest.raises(ReceiverINNValidationIPLenError), None),

        (None, PaymentType.FL, nullcontext(), None),
        (FL_INN, PaymentType.FL, nullcontext(), FL_INN),
        (LE_INN, PaymentType.FL, pytest.raises(ReceiverINNValidationFLLenError), None),

        (None, PaymentType.CHAMELEON, nullcontext(), None),
        (FL_INN, PaymentType.CHAMELEON, nullcontext(), FL_INN),
        (LE_INN, PaymentType.CHAMELEON, nullcontext(), LE_INN),

        (None, PaymentType.CUSTOMS, pytest.raises(ReceiverINNValidationNonEmptyError), None),
        (IP_INN, PaymentType.CUSTOMS, pytest.raises(ReceiverINNValidationLELenError), None),
        (LE_INN, PaymentType.CUSTOMS, nullcontext(), LE_INN),
    ]
)
def test_check_receiver_inn(
    value: Optional[str],
    payment_type: PaymentType,
    exception_handler: ContextManager,
    expected_value: str
) -> None:
    with exception_handler:
        assert expected_value == check_receiver_inn(value=value, payment_type=payment_type)


@pytest.mark.parametrize(
    'value, payment_type, for_third_person, exception_handler, expected_value',
    [
        ('01', PaymentType.FL, False, nullcontext(), None),
        (None, PaymentType.FL, False, nullcontext(), None),

        (None, PaymentType.CUSTOMS, False, pytest.raises(PayerStatusValidationNullNotAllowedError), None),
        ('06', PaymentType.CUSTOMS, True, pytest.raises(PayerStatusValidationCustoms05NotAllowedError), None),
        ('06', PaymentType.CUSTOMS, False, nullcontext(), '06'),
        ('31', PaymentType.CUSTOMS, True, nullcontext(), '31')
    ]
)
def test_check_payer_status(
    value: Optional[PayerStatus],
    payment_type: PaymentType,
    for_third_person: bool,
    exception_handler: ContextManager,
    expected_value: Optional[PayerStatus],
) -> None:
    with exception_handler:
        assert expected_value == check_payer_status(
            value=value,
            payment_type=payment_type,
            for_third_person=for_third_person,
        )


@pytest.mark.parametrize(
    'value, payment_type, payer_inn, exception_handler, expected_value',
    [
        (VALID_KPP, PaymentType.FL, VALID_INN, nullcontext(), None),
        (None, PaymentType.FL, VALID_INN, nullcontext(), None),

        (None, PaymentType.CUSTOMS, LE_INN, pytest.raises(PayerKPPValidationINN10EmptyNotAllowed), None),
        (VALID_KPP, PaymentType.CUSTOMS, IP_INN, pytest.raises(PayerKPPValidationINN12OnlyEmptyError), None),

        (VALID_KPP, PaymentType.CUSTOMS, LE_INN, nullcontext(), VALID_KPP),
    ]
)
def test_check_payer_kpp(
    value: Optional[KPP],
    payment_type: PaymentType,
    payer_inn: INN,
    exception_handler: ContextManager,
    expected_value: Optional[KPP],
) -> None:
    with exception_handler:
        assert expected_value == check_payer_kpp(value=value, payment_type=payment_type, payer_inn=payer_inn)


@pytest.mark.parametrize(
    'value, payment_type, exception_handler, expected_value',
    [
        (None, PaymentType.FL, nullcontext(), None),
        (VALID_KPP, PaymentType.FL, pytest.raises(ReceiverKPPValidationOnlyEmptyError), None),

        (None, PaymentType.FNS, pytest.raises(ReceiverKPPValidationEmptyNotAllowed), None),
        (FNS_KPP, PaymentType.FNS, nullcontext(), FNS_KPP),
        ('001234567', PaymentType.FNS, pytest.raises(ReceiverKPPValidationStartsWithZeros), None),
        (VALID_KPP, PaymentType.CUSTOMS, pytest.raises(ReceiverKPPValidationFTS), None),
        (VALID_KPP, PaymentType.FNS, pytest.raises(ReceiverKPPValidationFNS), None),
    ]
)
def test_check_receiver_kpp(
    value: Optional[KPP],
    payment_type: PaymentType,
    exception_handler: ContextManager,
    expected_value: Optional[KPP],
) -> None:
    with exception_handler:
        assert expected_value == check_receiver_kpp(value=value, payment_type=payment_type)


@pytest.mark.parametrize(
    'value, payment_type, exception_handler, expected_value',
    [
        (None, PaymentType.FL, nullcontext(), None),
        (None, PaymentType.BUDGET_OTHER, nullcontext(), None),
        (VALID_CBC, PaymentType.BUDGET_OTHER, nullcontext(), VALID_CBC),
        (None, PaymentType.FNS, pytest.raises(CBCValidationEmptyNotAllowed), None),
        (None, PaymentType.CUSTOMS, pytest.raises(CBCValidationEmptyNotAllowed), None),
        (VALID_CBC, PaymentType.FNS, nullcontext(), VALID_CBC),
    ]
)
def test_check_cbc(
    value: Optional[CBC],
    payment_type: PaymentType,
    exception_handler: ContextManager,
    expected_value: Optional[CBC],
) -> None:
    with exception_handler:
        assert expected_value == check_cbc(value=value, payment_type=payment_type)


@pytest.mark.parametrize(
    'value, payment_type, exception_handler, expected_value',
    [
        (None, PaymentType.FL, nullcontext(), None),
        (FTS_OKTMO, PaymentType.CUSTOMS, nullcontext(), FTS_OKTMO),
        (None, PaymentType.BUDGET_OTHER, nullcontext(), None),
        (None, PaymentType.FNS, pytest.raises(OKTMOValidationEmptyNotAllowed), None),
        ('0' * 8, PaymentType.FNS, pytest.raises(OKTMOValidationZerosNotAllowed), None),
        (VALID_OKTMO, PaymentType.CUSTOMS, pytest.raises(OKTMOValidationFTS), None),
        (VALID_OKTMO, PaymentType.FNS, nullcontext(), VALID_OKTMO),
    ]
)
def test_check_oktmo(
    value: Optional[OKTMO],
    payment_type: PaymentType,
    exception_handler: ContextManager,
    expected_value: Optional[OKTMO],
) -> None:
    with exception_handler:
        assert expected_value == check_oktmo(value=value, payment_type=payment_type)


@pytest.mark.parametrize(
    'value, payment_type, payer_status, exception_handler, expected_value',
    [
        (None, PaymentType.FL, '01', nullcontext(), None),
        (None, PaymentType.FNS, '01', nullcontext(), None),
        (None, PaymentType.FNS, '13', nullcontext(), None),
        (FTS_OKTMO, PaymentType.CUSTOMS, '13', nullcontext(), FTS_OKTMO),
        (None, PaymentType.BUDGET_OTHER, '13', nullcontext(), None),
        (None, PaymentType.FNS, '02', pytest.raises(OKTMOValidationFNSEmptyNotAllowed), None),
        (VALID_OKTMO, PaymentType.FNS, '06', nullcontext(), VALID_OKTMO),
    ]
)
def test_check_oktmo_with_payer_status(
    value: Optional[OKTMO],
    payment_type: PaymentType,
    payer_status: PayerStatus,
    exception_handler: ContextManager,
    expected_value: Optional[OKTMO],
) -> None:
    with exception_handler:
        assert expected_value == check_oktmo_with_payer_status(
            value=value,
            payment_type=payment_type,
            payer_status=payer_status
        )


@pytest.mark.parametrize(
    'value, payment_type, exception_handler, expected_value',
    [
        (None, PaymentType.FL, nullcontext(), None),
        (None, PaymentType.CUSTOMS, nullcontext(), None),
        (None, PaymentType.BUDGET_OTHER, nullcontext(), None),
        (None, PaymentType.FNS, nullcontext(), None),
        ('ПК', PaymentType.BUDGET_OTHER, nullcontext(), 'ПК'),
        ('AИ', PaymentType.CUSTOMS, pytest.raises(ReasonValidationValueErrorCustoms), None),
        ('ПК', PaymentType.FNS, pytest.raises(ReasonValidationValueErrorFNS), None),
    ]
)
def test_check_reason(
    value: Optional[Reason],
    payment_type: PaymentType,
    exception_handler: ContextManager,
    expected_value: Optional[Reason],
) -> None:
    with exception_handler:
        assert expected_value == check_reason(value=value, payment_type=payment_type)


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
        ('1', PaymentType.FNS, '01', pytest.raises(TaxPeriodValidationFNS01OnlyEmpty), None),
        ('1', PaymentType.FNS, '13', pytest.raises(TaxPeriodValidationFNS01OnlyEmpty), None),
        (None, PaymentType.FNS, '01', nullcontext(), None),
        (None, PaymentType.FNS, '13', nullcontext(), None),
        (None, PaymentType.FNS, '30', pytest.raises(TaxPeriodValidationFNSEmptyNotAllowed), None),
        ('1' * 10, PaymentType.FNS, '30', nullcontext(), '1' * 10),
    ]
)
def test_check_tax_period(
    value: Optional[TaxPeriod],
    payment_type: PaymentType,
    payer_status: PayerStatus,
    exception_handler: ContextManager,
    expected_value: Optional[TaxPeriod],
) -> None:
    with exception_handler:
        assert expected_value == check_tax_period(value=value, payment_type=payment_type, payer_status=payer_status)


@freeze_time(datetime(CHANGE_YEAR - 1, 12, 31))
@pytest.mark.parametrize(
    'value, payment_type, payer_status, exception_handler, expected_value',
    [
        (None, PaymentType.FNS, '02', pytest.raises(TaxPeriodValidationFNS02EmptyNotAllowed), None),
        ('1' * 10, PaymentType.FNS, '02', nullcontext(), '1' * 10),
        ('1' * 9, PaymentType.FNS, '02', pytest.raises(TaxPeriodValidationFNSValueLenError), None),
    ]
)
def test_check_tax_period_before_2024(
    value: Optional[TaxPeriod],
    payment_type: PaymentType,
    payer_status: PayerStatus,
    exception_handler: ContextManager,
    expected_value: Optional[TaxPeriod],
) -> None:
    with exception_handler:
        assert expected_value == check_tax_period(value=value, payment_type=payment_type, payer_status=payer_status)


@parametrize_with_dict(
    [
        'value', 'payment_type', 'payer_status', 'receiver_account',
        'payer_inn', 'uin', 'reason', 'exception_handler', 'expected_value'
    ],
    [
        {
            'case_id': 1,
            'value': None,
            'payment_type': PaymentType.FL,
            'payer_status': '',
            'receiver_account': '',
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
            'receiver_account': '',
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
            'receiver_account': '',
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
            'receiver_account': '03212',
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
            'receiver_account': '03212',
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
            'receiver_account': '03212',
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
            'receiver_account': '03212',
            'payer_inn': VALID_INN,
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
            'receiver_account': '03212',
            'payer_inn': VALID_INN,
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
            'receiver_account': '03212',
            'payer_inn': VALID_INN,
            'uin': None,
            'reason': '',
            'exception_handler': pytest.raises(DocumentNumberValidationBOValueError),
            'expected_value': None,
        },
        {
            'case_id': 10,
            'value': '1',
            'payment_type': PaymentType.CUSTOMS,
            'payer_status': '24',
            'receiver_account': '03212',
            'payer_inn': VALID_INN,
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
            'receiver_account': '03212',
            'payer_inn': VALID_INN,
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
            'receiver_account': '03212',
            'payer_inn': VALID_INN,
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
            'receiver_account': '03212',
            'payer_inn': VALID_INN,
            'uin': None,
            'reason': 'ИЛ',
            'exception_handler': nullcontext(),
            'expected_value': '01',
        }
    ]
)
def test_check_document_number(
    value: Optional[DocumentNumber],
    payment_type: PaymentType,
    payer_status: Optional[PayerStatus],
    receiver_account: AccountNumber,
    payer_inn: Optional[INN],
    uin: Optional[UIN],
    reason: Optional[str],
    exception_handler: ContextManager,
    expected_value: Optional[DocumentNumber],
) -> None:
    with exception_handler:
        assert expected_value == check_document_number(
            value=value,
            payment_type=payment_type,
            payer_status=payer_status,
            receiver_account=receiver_account,
            payer_inn=payer_inn,
            uin=uin,
            reason=reason,
        )


@pytest.mark.parametrize(
    'value, payment_type, exception_handler, expected_value',
    [
        (None, PaymentType.FL, nullcontext(), None),
        ('1', PaymentType.FNS, pytest.raises(DocumentDateValidationFNSOnlyEmptyError), None),
        (None, PaymentType.FNS, nullcontext(), None),
        (None, PaymentType.CUSTOMS, nullcontext(), None),
        (None, PaymentType.BUDGET_OTHER, nullcontext(), None),
        ('1' * 11, PaymentType.CUSTOMS, pytest.raises(DocumentDateValidationCustomsLenError), None),
        ('1' * 10, PaymentType.CUSTOMS, nullcontext(), '1' * 10),
        ('1' * 11, PaymentType.BUDGET_OTHER, pytest.raises(DocumentDateValidationBOLenError), None),
        ('1' * 10, PaymentType.BUDGET_OTHER, nullcontext(), '1' * 10),
    ]
)
def test_check_document_date(
    value: Optional[TaxPeriod],
    payment_type: PaymentType,
    exception_handler: ContextManager,
    expected_value: Optional[TaxPeriod],
) -> None:
    with exception_handler:
        assert expected_value == check_document_date(value=value, payment_type=payment_type)


@pytest.mark.parametrize(
    'payment_type, for_third_person, exception_handler',
    [
        (PaymentType.FL, True, pytest.raises(BudgetPaymentForThirdPersonError)),
        (PaymentType.IP, True, pytest.raises(BudgetPaymentForThirdPersonError)),
        (PaymentType.LE, True, pytest.raises(BudgetPaymentForThirdPersonError)),
        (PaymentType.FNS, True, nullcontext()),
        (PaymentType.CUSTOMS, True, nullcontext()),
        (PaymentType.BUDGET_OTHER, True, nullcontext()),
        (PaymentType.FL, False, nullcontext()),
        (PaymentType.IP, False, nullcontext()),
        (PaymentType.LE, False, nullcontext()),
        (PaymentType.FNS, False, nullcontext()),
        (PaymentType.CUSTOMS, False, nullcontext()),
        (PaymentType.BUDGET_OTHER, False, nullcontext()),
    ]
)
def test_check_payment_type_and_for_third_person(
    payment_type: PaymentType,
    for_third_person: bool,
    exception_handler: ContextManager,
) -> None:
    with exception_handler:
        check_payment_type_and_for_third_person(
            payment_type=payment_type,
            for_third_person=for_third_person,
        )
