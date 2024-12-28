import re
from datetime import date
from typing import Optional

from vitya.payment_order.enums import PaymentType
from vitya.payment_order.errors import (  # DocumentNumberValidationBOValueError,
    AccountValidationBICValueError,
    BudgetPaymentForThirdPersonError,
    CBCValidationEmptyNotAllowed,
    DocumentDateValidationBOLenError,
    DocumentDateValidationCustomsLenError,
    DocumentDateValidationCustomsReasonValueError,
    DocumentDateValidationFNSOnlyEmptyError,
    DocumentNumberValidationBOEmptyNotAllowed,
    DocumentNumberValidationBOOnlyEmptyError,
    DocumentNumberValidationBOPayerStatus33OnlyEmptyError,
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
    PayerKPPValidationINN5EmptyNotAllowed,
    PayerKPPValidationINN10EmptyNotAllowed,
    PayerKPPValidationINN12OnlyEmptyError,
    PayerStatusValidationCustoms05NotAllowedError,
    PayerStatusValidationCustomsIncorrectDataError,
    PayerStatusValidationFNSIncorrectDataError,
    PayerStatusValidationNullNotAllowedError,
    PayerStatusValidationOtherIncorrectDataError,
    PaymentTypeValueError,
    PurposeCodeValidationChameleonError,
    PurposeCodeValidationFlError,
    PurposeCodeValidationNullError,
    PurposeValidationForThirdPersonError,
    PurposeValidationValueEmptyErrorForNonFNS,
    ReasonValidationValueErrorCustoms,
    ReasonValidationValueErrorFNS,
    ReceiverAccountValidationBICValueError,
    ReceiverAccountValidationBudgetOtherPayerStatusError,
    ReceiverAccountValidationBudgetPayerStatusError,
    ReceiverAccountValidationCustomsValueError,
    ReceiverAccountValidationFNSValueError,
    ReceiverINNValidationChameleonLenError,
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
    TaxPeriodValidationBOValueOnlyOneZeroAllowed,
    TaxPeriodValidationCustomsEmptyNotAllowed,
    TaxPeriodValidationCustomsValueLenError,
    TaxPeriodValidationFNS01OnlyEmpty,
    TaxPeriodValidationFNS02EmptyNotAllowed,
    TaxPeriodValidationFNSValueLenError,
    UINValidationBONotEmpty,
    UINValidationFNSNotValueZeroError,
    UINValidationFNSOrFTSLenError,
    UINValidationFNSValueZeroError,
    UINValidationValueBudget33PayerStatusIncorrectLength,
    UINValidationValueZeroError,
)
from vitya.payment_order.fields import (
    CBC,
    UIN,
    AccountNumber,
    DocumentDate,
    DocumentNumber,
    ForThirdPerson,
    OperationKind,
    PayerINN,
    PayerKPP,
    PayerStatus,
    Purpose,
    PurposeCode,
    Reason,
    ReceiverAccountNumber,
    ReceiverBIC,
    ReceiverINN,
    ReceiverKPP,
    TaxPeriod,
)
from vitya.payment_order.payments.constants import (
    CHANGE_YEAR,
    CUSTOMS_REASONS,
    CUSTOMS_RECEIVER_ACCOUNT_NUMBER,
    DOCUMENT_NUMBERS,
    FNS_KPP,
    FNS_RECEIVER_ACCOUNT_NUMBER,
    FNS_TAX_PAYER_STATUSES,
    FTS_KPP,
    FTS_OKTMO,
    FTS_TAX_PAYER_STATUSES,
    OTHER_OKTMO_RECEIVER_ACCOUNT_PREFIXES,
    OTHER_OKTMO_RECEIVER_ACCOUNT_PREFIXES_2,
)
from vitya.pydantic_fields import BIC, OKTMO


def check_account_by_bic(
    account_number: AccountNumber,
    bic: BIC,
) -> None:
    _sum = 0
    for c, v in zip(bic[-3:] + account_number, [7, 1, 3] * 8):
        _sum += int(c) * v
    if _sum % 10 != 0:
        raise AccountValidationBICValueError


def check_receiver_account(
    value: ReceiverAccountNumber,
    payment_type: PaymentType,
    receiver_bic: ReceiverBIC,
) -> str:
    if payment_type == PaymentType.FNS:
        if value != FNS_RECEIVER_ACCOUNT_NUMBER:
            raise ReceiverAccountValidationFNSValueError
    elif not payment_type.is_budget:
        try:
            check_account_by_bic(account_number=value, bic=receiver_bic)
        except AccountValidationBICValueError as e:
            raise ReceiverAccountValidationBICValueError from e
    return value


def check_receiver_account_with_payment_type(
    value: ReceiverAccountNumber,
    payment_type: PaymentType,
) -> str:
    if payment_type == PaymentType.CUSTOMS and value != CUSTOMS_RECEIVER_ACCOUNT_NUMBER:
        raise ReceiverAccountValidationCustomsValueError
    return value


def check_receiver_account_with_payment_type_and_payer_status(
    value: ReceiverAccountNumber,
    payment_type: PaymentType,
    payer_status: Optional[PayerStatus],
) -> str:
    if (
        payment_type.is_budget
        and payer_status in ['01', '02', '04', '06', '07', '13', '16', '17', '28', '30']
        and not value.startswith('03100')
    ):
        raise ReceiverAccountValidationBudgetPayerStatusError

    elif (
        payment_type == PaymentType.BUDGET_OTHER
        and payer_status == '31'
        and not value.startswith('03212')
    ):
        raise ReceiverAccountValidationBudgetOtherPayerStatusError

    return value


def check_operation_kind(
    value: OperationKind,
    payment_type: PaymentType
) -> OperationKind:
    if payment_type.is_budget and value not in {'01', '02', '06'}:
        raise OperationKindValidationBudgetValueError
    return value


def check_purpose_code(
    value: Optional[PurposeCode],
    payment_type: PaymentType,
) -> Optional[PurposeCode]:
    if payment_type not in (PaymentType.FL, PaymentType.CHAMELEON):
        if value is not None:
            raise PurposeCodeValidationNullError
        return None
    if value is not None and value not in {1, 2, 3, 4, 5}:
        if payment_type == PaymentType.FL:
            raise PurposeCodeValidationFlError
        raise PurposeCodeValidationChameleonError
    return value


def check_uin(
    value: Optional[UIN],
    receiver_account: ReceiverAccountNumber,
    payment_type: PaymentType,
    payer_status: Optional[PayerStatus],
    payer_inn: Optional[PayerINN],
) -> Optional[UIN]:
    if not payment_type.is_budget:
        return None

    if payer_status == '31' and value is None:
        raise UINValidationValueZeroError

    if (
        payment_type.is_budget and payer_status == '33'
        and (not value or len(value) not in [20, 25] or value == '0' * len(value))
    ):
        raise UINValidationValueBudget33PayerStatusIncorrectLength

    if value is not None and payment_type in {PaymentType.FNS, PaymentType.CUSTOMS} and len(value) not in [25, 20]:
        raise UINValidationFNSOrFTSLenError

    if payment_type == PaymentType.BUDGET_OTHER:
        if receiver_account.startswith('03212') and value is None:
            raise UINValidationBONotEmpty
        return value

    if payment_type == PaymentType.FNS:
        if payer_status == '13' and payer_inn is None and value is None:
            raise UINValidationFNSValueZeroError
        if payer_status == '02' and date.today().year < CHANGE_YEAR:
            if value is not None:
                raise UINValidationFNSNotValueZeroError
            return value
    return value


def check_purpose(
    value: Optional[Purpose],
    payment_type: PaymentType,
) -> Optional[Purpose]:
    if payment_type == PaymentType.FNS and not value:
        return Purpose('0')

    if payment_type != PaymentType.FNS and not value:
        raise PurposeValidationValueEmptyErrorForNonFNS

    return value


def check_payer_inn(
    value: Optional[PayerINN],
    payment_type: PaymentType,
    payer_status: Optional[PayerStatus],
    for_third_person: ForThirdPerson,
) -> Optional[PayerINN]:
    if not payment_type.is_budget:
        return value

    if value is None:
        if payment_type == PaymentType.BUDGET_OTHER:
            return None
        elif payment_type == PaymentType.FNS:
            return None
        elif payment_type == PaymentType.CUSTOMS and payer_status == '30':
            return None
        raise PayerINNValidationEmptyNotAllowedError

    if payment_type == PaymentType.CUSTOMS:
        if payer_status == '06' and for_third_person and len(value) != 10:
            raise PayerINNValidationCustomsLen10Error

        if payer_status in {'16', '17'} and len(value) != 12:
            raise PayerINNValidationCustomsLen12Error

    if value.startswith('00'):
        raise PayerINNValidationStartWithZerosError

    return value


def check_payer_inn_with_uin_and_receiver_account(
    value: Optional[PayerINN],
    payment_type: PaymentType,
    payer_status: Optional[PayerStatus],
    receiver_account: Optional[ReceiverAccountNumber],
    uin: Optional[UIN],
) -> Optional[PayerINN]:
    if value is None and payment_type == PaymentType.FNS:
        if not (
            payer_status == '13'
            and receiver_account is not None
            and receiver_account.startswith('03100')
            and uin is not None
            and len(uin) in [20, 25]
        ):
            raise PayerINNValidationEmptyNotAllowedError

    return None


def check_receiver_inn(
    value: Optional[ReceiverINN],
    payment_type: PaymentType,
) -> Optional[ReceiverINN]:
    if payment_type in [
        PaymentType.CUSTOMS,
        PaymentType.FNS,
        PaymentType.BUDGET_OTHER,
        PaymentType.LE,
        PaymentType.IP
    ] and value is None:
        raise ReceiverINNValidationNonEmptyError
    if payment_type in [
        PaymentType.CUSTOMS,
        PaymentType.FNS,
        PaymentType.BUDGET_OTHER,
        PaymentType.LE
    ] and (value is None or len(value) != 10):
        raise ReceiverINNValidationLELenError

    if payment_type == PaymentType.IP:
        if value is None or len(value) != 12:
            raise ReceiverINNValidationIPLenError
    elif payment_type == PaymentType.FL:
        if value is not None and len(value) != 12:
            raise ReceiverINNValidationFLLenError
    elif payment_type == PaymentType.CHAMELEON:
        if value is not None and len(value) not in (10, 12):
            raise ReceiverINNValidationChameleonLenError

    return value


def check_payment_type_and_for_third_person(
    payment_type: PaymentType,
    for_third_person: ForThirdPerson,
) -> None:
    if for_third_person and not payment_type.is_budget:
        raise BudgetPaymentForThirdPersonError


def check_purpose_for_third_person(
    value: Optional[Purpose],
    for_third_person: ForThirdPerson,
) -> Optional[Purpose]:
    if not for_third_person:
        return value

    if not value or not re.match(r'^\d+\/\/[a-zA-Zа-яА-ЯёЁ\s\W]+\/\/[а-яА-ЯёЁ\s!-~№]*$', value):
        raise PurposeValidationForThirdPersonError

    return value


def check_payer_status(
    value: Optional[PayerStatus],
    payment_type: PaymentType,
    for_third_person: Optional[ForThirdPerson],
) -> Optional[PayerStatus]:
    if not payment_type.is_budget:
        return None

    if value is None:
        raise PayerStatusValidationNullNotAllowedError

    if payment_type == PaymentType.FNS and value not in FNS_TAX_PAYER_STATUSES:
        raise PayerStatusValidationFNSIncorrectDataError

    if payment_type == PaymentType.CUSTOMS and value not in FTS_TAX_PAYER_STATUSES:
        raise PayerStatusValidationCustomsIncorrectDataError

    if payment_type == PaymentType.BUDGET_OTHER and value in FNS_TAX_PAYER_STATUSES + FTS_TAX_PAYER_STATUSES:
        raise PayerStatusValidationOtherIncorrectDataError

    if payment_type == PaymentType.CUSTOMS and for_third_person == False and value == '06':  # noqa
        raise PayerStatusValidationCustoms05NotAllowedError

    return value


def check_payer_kpp(
    value: Optional[PayerKPP],
    payment_type: PaymentType,
    payer_inn: Optional[PayerINN],
    payer_status: Optional[PayerStatus],
) -> Optional[PayerKPP]:
    if not payment_type.is_budget:
        return None

    if payer_inn is not None and len(payer_inn) == 5 and value is None:
        raise PayerKPPValidationINN5EmptyNotAllowed
    elif payer_inn is not None and len(payer_inn) == 10 and value is None and payer_status != '01':
        raise PayerKPPValidationINN10EmptyNotAllowed
    elif payer_inn is not None and len(payer_inn) == 12 and value is not None:
        raise PayerKPPValidationINN12OnlyEmptyError
    return value


def check_receiver_kpp(
    value: Optional[ReceiverKPP],
    payment_type: PaymentType,
) -> Optional[ReceiverKPP]:
    if payment_type in {PaymentType.FL, PaymentType.IP}:
        if value is not None:
            raise ReceiverKPPValidationOnlyEmptyError
        return None
    if payment_type in {PaymentType.LE, PaymentType.CHAMELEON}:
        return value
    if value is None:
        raise ReceiverKPPValidationEmptyNotAllowed
    if value.startswith('00'):
        raise ReceiverKPPValidationStartsWithZeros
    if payment_type == PaymentType.FNS and value != FNS_KPP:
        raise ReceiverKPPValidationFNS
    if payment_type == PaymentType.CUSTOMS and value != FTS_KPP:
        raise ReceiverKPPValidationFTS
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
) -> Optional[OKTMO]:
    if not payment_type.is_budget:
        return None

    if payment_type == PaymentType.CUSTOMS and value != FTS_OKTMO:
        raise OKTMOValidationFTS

    if payment_type in {PaymentType.FNS, PaymentType.BUDGET_OTHER} and value is None:
        return None

    if value is None:
        raise OKTMOValidationEmptyNotAllowed

    if all(c == '0' for c in value):
        raise OKTMOValidationZerosNotAllowed
    return value


def check_oktmo_with_payer_status(
    value: Optional[OKTMO],
    payment_type: PaymentType,
    payer_status: Optional[PayerStatus],
) -> Optional[OKTMO]:
    if payment_type == PaymentType.FNS and payer_status in {'01', '13'} and value is None:
        return None

    if (
        payment_type == PaymentType.FNS and
        payer_status == '02' and
        value is None and
        date.today().year < CHANGE_YEAR
    ):
        raise OKTMOValidationFNSEmptyNotAllowed

    return value


def check_oktmo_with_receiver_account_number(
    value: Optional[OKTMO],
    payment_type: PaymentType,
    receiver_account_number: ReceiverAccountNumber,
) -> Optional[OKTMO]:
    if payment_type == PaymentType.BUDGET_OTHER and (value is None or value == '0'):
        if (
            receiver_account_number[:5] in OTHER_OKTMO_RECEIVER_ACCOUNT_PREFIXES
            or (
                receiver_account_number[:5] in OTHER_OKTMO_RECEIVER_ACCOUNT_PREFIXES_2
                and receiver_account_number[13] == '4'
            )
        ):
            return None
        raise OKTMOValidationEmptyNotAllowed

    return value


def check_reason(
    value: Optional[Reason],
    payment_type: PaymentType,
) -> Optional[Reason]:
    if not payment_type.is_budget:
        return None

    if payment_type.is_budget and (value is None or value == '0'):
        return None
    if payment_type == PaymentType.CUSTOMS and value not in CUSTOMS_REASONS:
        raise ReasonValidationValueErrorCustoms
    if payment_type == PaymentType.FNS and value and value != '0':
        raise ReasonValidationValueErrorFNS
    return value


def check_tax_period(
    value: Optional[TaxPeriod],
    payment_type: PaymentType,
    payer_status: Optional[PayerStatus],
) -> Optional[TaxPeriod]:
    if not payment_type.is_budget:
        return None

    if payment_type == PaymentType.BUDGET_OTHER:
        if value is None:
            return None
        elif len(value) > 10:
            raise TaxPeriodValidationBOValueLenError
        elif value == '0' * len(value):
            raise TaxPeriodValidationBOValueOnlyOneZeroAllowed
        return value
    elif payment_type == PaymentType.CUSTOMS:
        if value is None:
            raise TaxPeriodValidationCustomsEmptyNotAllowed
        elif len(value) != 8:
            raise TaxPeriodValidationCustomsValueLenError
        return value
    else:
        if (
            payer_status == '02' and
            value is None and
            date.today().year < CHANGE_YEAR
        ):
            raise TaxPeriodValidationFNS02EmptyNotAllowed
        if payer_status in {'01', '13'}:
            if value is not None:
                raise TaxPeriodValidationFNS01OnlyEmpty
            return None

        if payer_status == '02' and len(value or '') != 10 and date.today().year < CHANGE_YEAR:
            raise TaxPeriodValidationFNSValueLenError
        return value


def check_document_number(
    value: Optional[DocumentNumber],
    payment_type: PaymentType,
    reason: Optional[Reason],
    payer_status: Optional[PayerStatus],
    uin: Optional[UIN],
    payer_inn: Optional[PayerINN],
) -> Optional[DocumentNumber]:
    if not payment_type.is_budget:
        return None

    if payer_status == '31':
        if value is not None:
            raise DocumentNumberValidationBOOnlyEmptyError
        return None

    if payment_type == PaymentType.FNS:
        if value is not None:
            raise DocumentNumberValidationFNSOnlyEmptyError
        return None
    elif payment_type == PaymentType.BUDGET_OTHER:
        if payer_status == '33' and date.today().year >= CHANGE_YEAR:
            if value is not None:
                raise DocumentNumberValidationBOPayerStatus33OnlyEmptyError
            return None
        if payer_status == '24' and payer_inn is None and uin is None and value is None:
            raise DocumentNumberValidationBOEmptyNotAllowed
        if value is not None:
            if len(value) > 15:
                raise DocumentNumberValidationBOValueLenError
            if (
                payer_status == '24' and (
                    len(value) < 3 or value[2] != ';' or value[:2] not in DOCUMENT_NUMBERS
                )
            ):
                raise DocumentNumberValidationBOValueError
        return value
    elif payment_type == PaymentType.CUSTOMS:
        if reason == '00' and value is not None and value not in ['00', '0']:
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
        if value is not None and value != '0':
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


def check_document_date_with_reason(
    value: Optional[DocumentDate],
    payment_type: PaymentType,
    reason: Reason,
) -> Optional[DocumentDate]:
    if payment_type == PaymentType.CUSTOMS and reason == '00':
        if not (value is None or value in ['0', '00']):
            raise DocumentDateValidationCustomsReasonValueError
    return value
