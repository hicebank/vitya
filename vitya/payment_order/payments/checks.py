import re
from typing import Optional

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
    PayeeAccountValidationBICValueError,
    PayeeAccountValidationFNSValueError,
    PayeeINNValidationFLLenError,
    PayeeINNValidationIPLenError,
    PayeeINNValidationLELenError,
    PayeeINNValidationNonEmptyError,
    PayeeKPPValidationEmptyNotAllowed,
    PayeeKPPValidationOnlyEmptyError,
    PayeeKPPValidationStartsWithZeros,
    PayerINNValidationCustomsLen10Error,
    PayerINNValidationCustomsLen12Error,
    PayerINNValidationEmptyNotAllowedError,
    PayerINNValidationStartWithZerosError,
    PayerKPPValidationINN10EmptyNotAllowed,
    PayerKPPValidationINN12OnlyEmptyError,
    PayerStatusValidationCustoms05NotAllowedError,
    PayerStatusValidationNullNotAllowedError,
    PaymentTypeValueError,
    PurposeCodeValidationFlError,
    PurposeCodeValidationNullError,
    PurposeValidationIPNDSError,
    ReasonValidationFNSOnlyEmptyError,
    ReasonValidationValueErrorCustoms,
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
from vitya.payment_order.payments.constants import (
    CUSTOMS_REASONS,
    DOCUMENT_NUMBERS,
    FNS_PAYEE_ACCOUNT_NUMBER,
)
from vitya.pydantic_fields import BIC, INN, KPP, OKTMO


def check_account_by_bic(
    account_number: AccountNumber,
    bic: BIC,
) -> None:
    _sum = 0
    for c, v in zip(bic[-3:] + account_number, [7, 1, 3] * 8):
        _sum += int(c) * v
    if _sum % 10 != 0:
        raise AccountValidationBICValueError


def check_payee_account(
    value: AccountNumber,
    payment_type: PaymentType,
    payee_bic: BIC,
) -> str:
    if payment_type == PaymentType.FNS:
        if value != FNS_PAYEE_ACCOUNT_NUMBER:
            raise PayeeAccountValidationFNSValueError
    elif not payment_type.is_budget:
        try:
            check_account_by_bic(account_number=value, bic=payee_bic)
        except AccountValidationBICValueError as e:
            raise PayeeAccountValidationBICValueError from e
    return value


def check_operation_kind(
    value: OperationKind,
    payment_type: PaymentType
) -> OperationKind:
    if payment_type.is_budget:
        if value not in {'01', '02', '06'}:
            raise OperationKindValidationBudgetValueError
    return value


def check_purpose_code(
    value: Optional[int],
    payment_type: PaymentType,
) -> Optional[int]:
    if payment_type != PaymentType.FL:
        if value is not None:
            raise PurposeCodeValidationNullError
        return None
    if value is not None and value not in {1, 2, 3, 4, 5}:
        raise PurposeCodeValidationFlError
    return value


def check_uin(
    value: Optional[UIN],
    payment_type: PaymentType,
    payer_status: PayerStatus,
    payer_inn: Optional[str],
) -> Optional[str]:
    if not payment_type.is_budget:
        return None

    if payer_status == '31' and value is None:
        raise UINValidationValueZeroError

    if payment_type == PaymentType.BUDGET_OTHER:
        return value

    if payment_type == PaymentType.FNS:
        if payer_status == '13' and payer_inn is None and value is None:
            raise UINValidationFNSValueZeroError
        if payer_status == '02':
            if value is not None:
                raise UINValidationFNSNotValueZeroError
            return value
    return value


def check_purpose(
    value: Optional[Purpose],
    payment_type: PaymentType,
) -> Optional[str]:
    if value is None:
        return None

    if payment_type == PaymentType.IP:
        if not re.search(r'(?i)\bНДС\b', value):
            raise PurposeValidationIPNDSError
    return value


def check_payer_inn(
    value: Optional[INN],
    payment_type: PaymentType,
    payer_status: PayerStatus,
    for_third_face: bool = False,
) -> Optional[str]:
    if not payment_type.is_budget:
        return value

    if value is None:
        if payment_type == PaymentType.BUDGET_OTHER:
            return None
        elif payment_type == PaymentType.FNS and payer_status == '13':
            return None
        elif payment_type == PaymentType.CUSTOMS and payer_status == '30':
            return None
        raise PayerINNValidationEmptyNotAllowedError

    if payment_type == PaymentType.CUSTOMS:
        if payer_status == '06' and for_third_face and len(value) != 10:
            raise PayerINNValidationCustomsLen10Error

        if payer_status in {'16', '17'} and len(value) != 12:
            raise PayerINNValidationCustomsLen12Error

    if value.startswith('00'):
        raise PayerINNValidationStartWithZerosError

    return value


def check_payee_inn(
    value: Optional[INN],
    payment_type: PaymentType,
) -> Optional[str]:
    if payment_type == PaymentType.IP:
        if value is None or len(value) != 12:
            raise PayeeINNValidationIPLenError
        return value
    elif payment_type == PaymentType.FL:
        if value is not None and len(value) != 12:
            raise PayeeINNValidationFLLenError
        return value
    if value is None:
        raise PayeeINNValidationNonEmptyError
    elif len(value) != 10:
        raise PayeeINNValidationLELenError
    return value


def check_payer_status(
    value: Optional[PayerStatus],
    payment_type: PaymentType,
    for_third_face: bool,
) -> Optional[str]:
    if not payment_type.is_budget:
        return None

    if value is None:
        raise PayerStatusValidationNullNotAllowedError

    if payment_type == PaymentType.CUSTOMS and for_third_face and value == '06':
        raise PayerStatusValidationCustoms05NotAllowedError

    return value


def check_payer_kpp(
    value: Optional[KPP],
    payment_type: PaymentType,
    payer_inn: str,
) -> Optional[KPP]:
    if not payment_type.is_budget:
        return None

    if len(payer_inn) == 10 and value is None:
        raise PayerKPPValidationINN10EmptyNotAllowed
    elif len(payer_inn) == 12 and value is not None:
        raise PayerKPPValidationINN12OnlyEmptyError
    return value


def check_payee_kpp(
    value: Optional[KPP],
    payment_type: PaymentType,
) -> Optional[KPP]:
    if payment_type in {PaymentType.FL, PaymentType.IP}:
        if value is not None:
            raise PayeeKPPValidationOnlyEmptyError
        return None

    if value is None:
        raise PayeeKPPValidationEmptyNotAllowed
    if value.startswith('00'):
        raise PayeeKPPValidationStartsWithZeros
    return value


def check_cbc(
    value: Optional[CBC],
    payment_type: PaymentType,
) -> Optional[CBC]:
    if not payment_type.is_budget:
        return None

    if payment_type == PaymentType.BUDGET_OTHER and value is None:
        return None

    if payment_type in {PaymentType.FNS, PaymentType.CUSTOMS} and value is None:
        raise CBCValidationEmptyNotAllowed

    return value


def check_oktmo(
    value: Optional[OKTMO],
    payment_type: PaymentType,
    payer_status: PayerStatus,
) -> Optional[OKTMO]:
    if not payment_type.is_budget:
        return None

    if payment_type == PaymentType.FNS and payer_status in {'01', '13'} and value is None:
        return None

    if payment_type in {PaymentType.CUSTOMS, PaymentType.BUDGET_OTHER} and value is None:
        return None

    if payment_type == PaymentType.FNS and payer_status == '02' and value is None:
        raise OKTMOValidationFNSEmptyNotAllowed

    if value is None:
        raise OKTMOValidationEmptyNotAllowed

    if all(c == '0' for c in value):
        raise OKTMOValidationZerosNotAllowed
    return value


def check_reason(
    value: Optional[Reason],
    payment_type: PaymentType,
) -> Optional[Reason]:
    if not payment_type.is_budget:
        return None

    if payment_type in {PaymentType.CUSTOMS, PaymentType.BUDGET_OTHER} and value is None:
        return None
    if payment_type == PaymentType.FNS:
        if value is not None:
            raise ReasonValidationFNSOnlyEmptyError
        return None
    if payment_type == PaymentType.CUSTOMS and value not in CUSTOMS_REASONS:
        raise ReasonValidationValueErrorCustoms
    return value


def check_tax_period(
    value: Optional[TaxPeriod],
    payment_type: PaymentType,
    payer_status: PayerStatus,
) -> Optional[TaxPeriod]:
    if not payment_type.is_budget:
        return None

    if payment_type == PaymentType.BUDGET_OTHER:
        if value is None:
            return None
        elif len(value) > 10:
            raise TaxPeriodValidationBOValueLenError
        return value
    elif payment_type == PaymentType.CUSTOMS:
        if value is None:
            raise TaxPeriodValidationCustomsEmptyNotAllowed
        elif len(value) != 8:
            raise TaxPeriodValidationCustomsValueLenError
        return value
    else:
        if payer_status == '02' and value is None:
            raise TaxPeriodValidationFNS02EmptyNotAllowed
        if payer_status in {'01', '13'}:
            if value is not None:
                raise TaxPeriodValidationFNS01OnlyEmpty
            return None

        if value is None:
            raise TaxPeriodValidationFNSEmptyNotAllowed
        elif len(value) != 10:
            raise TaxPeriodValidationFNSValueLenError
        return value


def check_document_number(
    value: Optional[DocumentNumber],
    payment_type: PaymentType,
    reason: Optional[Reason],
    payer_status: Optional[PayerStatus],
    payee_account: AccountNumber,
    uin: Optional[UIN],
    payer_inn: Optional[INN],
) -> Optional[DocumentNumber]:
    if not payment_type.is_budget:
        return None

    if payment_type == PaymentType.FNS:
        if value is not None:
            raise DocumentNumberValidationFNSOnlyEmptyError
        return None
    elif payment_type == PaymentType.BUDGET_OTHER:
        if payee_account.startswith('03212') and payer_status == '31' and uin is not None:
            if value is not None:
                raise DocumentNumberValidationBOOnlyEmptyError
            return None

        if payer_status == '24' and payer_inn is None and uin is None and value is None:
            raise DocumentNumberValidationBOEmptyNotAllowed
        if value is not None:
            if len(value) > 15:
                raise DocumentNumberValidationBOValueLenError
            if len(value) < 3 or value[2] != ";" or value[:2] not in DOCUMENT_NUMBERS:
                raise DocumentNumberValidationBOValueError
        return value
    elif payment_type == PaymentType.CUSTOMS:
        if reason == '00' and (value is None or value != '00'):
            raise DocumentNumberValidationCustoms00ValueError
        if reason in {'ПК', 'УВ', 'ТГ', 'ТБ', 'ТД', 'ПВ'} and value and len(value) > 7:
            raise DocumentNumberValidationCustomsValueLen7Error
        if (
            reason in {'ИЛ', 'ИН', 'ПБ', 'КЭ'}
            and (
                value is None or len(value) > 15
            )
        ):
            raise DocumentNumberValidationCustomsValueLen15Error
        return value
    raise PaymentTypeValueError(payment_type=payment_type)  # pragma: no cover


def check_document_date(
    value: Optional[DocumentDate],
    payment_type: PaymentType,
) -> Optional[DocumentDate]:
    if not payment_type.is_budget:
        return None

    if payment_type == PaymentType.FNS:
        if value is not None:
            raise DocumentDateValidationFNSOnlyEmptyError
        return None
    else:
        if value is None:
            return None
        if payment_type == PaymentType.CUSTOMS:
            if len(value) != 10:
                raise DocumentDateValidationCustomsLenError
            return value
        else:
            if len(value) > 10:
                raise DocumentDateValidationBOLenError
            return value
