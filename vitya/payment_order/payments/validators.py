import re
from _decimal import Decimal
from datetime import date
from typing import Any, Optional

from vitya.payment_order.enums import PaymentType
from vitya.payment_order.errors import (
    NumberValidationLenError, PayeeINNValidationFLenError, PayerINNValidationEmptyNotAllowedError,
    PayerINNValidationFiveOnlyZerosError,
    INNValidationLenError,
    PayerINNValidationStartWithZerosError, PayerINNValidationTMSLen10Error, PayerINNValidationTMSLen12Error,
    OperationKindValidationBudgetValueError,
    OperationKindValidationValueError,
    PurposeCodeValidationFlError,
    PurposeCodeValidationNullError, PurposeValidationCharactersError, PurposeValidationIPNDSError,
    UINValidationBOLenError,
    UINValidationControlSumError, UINValidationDigitsOnlyError,
    UINValidationFNSNotValueZeroError, UINValidationFNSValueZeroError, UINValidationLenError,
    UINValidationOnlyZeroError, UINValidationValueZeroError,
)
from vitya.payment_order.fields import Payee, Payer, PaymentOrder
from vitya.payment_order.payments.helpers import CHARS_FOR_PURPOSE, REPLACE_CHARS_FOR_SPACE
from vitya.pydantic_fields import Bic


def validate_payment_data(
    _type: PaymentType,
    *,
    name: str,
    form: str,
    number: str,
    date: date,
    kind: str,
    amount: Decimal,
    amount_str: str,
    payer_name: Payer,
    payer_account: str,
    payer_bank_name: Optional[str],
    payer_bank_bic: Bic,
    payer_bank_account: Optional[str],
    payee_bank_name: Optional[str],
    payee_bank_bic: Bic,
    payee_bank_account: Optional[str],
    payee_name: Payee,
    payee_account: str,
    operation_kind: str,
    payment_expire_days: Optional[int],
    purpose_code: Optional[int],
    payment_order: PaymentOrder,
    uin: str,
    reserve_field: Optional[str],
    purpose: Optional[str],
    payer_inn: str,
    payee_inn: str,
    bank_income_date: date,
    bank_outcome_date: date,
    payer_status: str,
    payer_kpp: str,
    payee_kpp: str,
    cbc: Optional[str],
    oktmo: Optional[str],
    reason: Optional[str],
    tax_period: Optional[str],
    document_number: Optional[str],
    document_date: Optional[date],
) -> dict[str, Any]:
    number = validate_number(value=number)

    operation_kind = validate_operation_kind(_type=_type, value=operation_kind)
    purpose_code = validate_purpose_code(_type=_type, value=purpose_code)

    payer_inn = validate_payer_inn(_type=_type, payer_status=payer_status, value=payer_inn)
    payee_inn = validate_payee_inn(_type=_type, value=payee_inn)
    uin = validate_uin(_type=_type, value=uin, payer_status=payer_status, payer_inn=payer_inn)

    purpose = validate_purpose(_type=_type, value=purpose)
    return {
        '_type': _type,
        'name': name,
        'form': form,
        'number': number,
        'date': date,
        'kind': kind,
        'amount': amount,
        'amount_str': amount_str,
        'payer_name': payer_name,
        'payer_account': payer_account,
        'payer_bank_name': payer_bank_name,
        'payer_bank_bic': payer_bank_bic,
        'payer_bank_account': payer_bank_account,
        'payee_bank_name': payee_bank_name,
        'payee_bank_bic': payee_bank_bic,
        'payee_bank_account': payee_bank_account,
        'payee_name': payee_name,
        'payee_account': payee_account,
        'operation_kind': operation_kind,
        'payment_expire_days': payment_expire_days,
        'purpose_code': purpose_code,
        'payment_order': payment_order,
        'uin': uin,
        'reserve_field': reserve_field,
        'purpose': purpose,
        'payer_inn': payer_inn,
        'payee_inn': payee_inn,
        'bank_income_date': bank_income_date,
        'bank_outcome_date': bank_outcome_date,
        'payer_status': payer_status,
        'payer_kpp': payer_kpp,
        'payee_kpp': payee_kpp,
        'cbc': cbc,
        'oktmo': oktmo,
        'reason': reason,
        'tax_period': tax_period,
        'document_number': document_number,
        'document_date': document_date,
    }


def validate_number(
    value: str,
) -> str:
    if len(value) > 6:
        raise NumberValidationLenError
    return value


def validate_operation_kind(
    _type: PaymentType,
    value: str
) -> str:
    if _type.is_budget:
        if value not in {'01', '02', '06'}:
            raise OperationKindValidationBudgetValueError
    if len(value) != 2:
        raise OperationKindValidationValueError
    return value


def validate_purpose_code(
    _type: PaymentType,
    value: Optional[int],
) -> Optional[int]:
    """
    Назначение платежа кодовое (20)
    """
    if _type != PaymentType.fl:
        if value is not None:
            raise PurposeCodeValidationNullError
        return value
    if value not in {1, 2, 3, 4, 5}:
        raise PurposeCodeValidationFlError
    return value


def validate_uin_control_sum(
    value: str
) -> None:
    if not value.isdigit():
        raise UINValidationDigitsOnlyError
    if len(value) != 20 and len(value) != 25:
        return

    count = 1
    sum_ = 0
    for c in value[:-1:]:
        if count > 10:
            count = 1
        sum_ += int(c) * count
        count += 1

    if sum_ == 0:
        raise UINValidationOnlyZeroError

    mod_11 = sum_ % 11
    if mod_11 != 10:
        if mod_11 != int(value[-1]):
            raise UINValidationControlSumError

    count = 3
    sum_ = 0
    for c in value[:-1:]:
        if count > 10:
            count = 1
        sum_ += int(c) * count
        count += 1
    mod_11 = sum_ % 11
    mod_11 = 0 if mod_11 == 10 else mod_11
    if mod_11 != int(value[-1]):
        raise UINValidationControlSumError


def validate_uin(
    _type: PaymentType,
    value: Optional[str],
    payer_status: str,
    payer_inn: str,
) -> str:
    value = value or '0'
    if not value.isdigit():
        raise UINValidationDigitsOnlyError

    len_value = len(value)
    if not _type.is_budget:
        return '0'

    if payer_status == '31' and value == '0':
        raise UINValidationValueZeroError

    if _type == PaymentType.bo:
        if not (len_value == 4 or len_value == 20 or len_value == 25):
            raise UINValidationBOLenError
        validate_uin_control_sum(value)
        return value

    if _type == PaymentType.fns:
        if payer_status == '13' and payer_inn == '' and value == '0':
            raise UINValidationFNSValueZeroError
        if payer_status == '02':
            if value != '0':
                raise UINValidationFNSNotValueZeroError
            return value

    if not (len_value == 20 or len_value == 25):
        raise UINValidationLenError

    validate_uin_control_sum(value)
    return value


def validate_purpose(
    _type: PaymentType,
    value: str,
) -> str:
    value = value or '0'
    spaces_set = set(REPLACE_CHARS_FOR_SPACE)
    allowed_chars_set = set(CHARS_FOR_PURPOSE)
    replaced_space_value = ''.join(
        list(map(lambda x: x if x not in spaces_set else ' ', value))
    )
    for c in replaced_space_value:
        if c not in allowed_chars_set:
            raise PurposeValidationCharactersError

    if _type == PaymentType.ip:
        if not re.search(r'(?i)\bНДС\b', replaced_space_value):
            raise PurposeValidationIPNDSError
    return value


def validate_payer_inn(
    _type: PaymentType,
    payer_status: str,
    value: str,
) -> str:
    if not _type.is_budget:
        if not value.isdigit():
            raise UINValidationDigitsOnlyError
        return value

    if value == '':
        if _type == PaymentType.bo:
            return ''
        elif _type == PaymentType.fns and payer_status == '13':
            return ''
        elif _type == PaymentType.tms and payer_status == '30':
            return ''
        raise PayerINNValidationEmptyNotAllowedError

    if not value.isdigit():
        raise UINValidationDigitsOnlyError

    if len(value) not in {5, 10, 12}:
        raise INNValidationLenError

    if _type == PaymentType.tms:
        if payer_status == '06' and len(value) != 10:
            raise PayerINNValidationTMSLen10Error

        if payer_status in {'16', '17'} and len(value) != 12:
            raise PayerINNValidationTMSLen12Error

    if value.startswith('00'):
        raise PayerINNValidationStartWithZerosError

    if len(value) == 5 and all(c == '0' for c in value):
        raise PayerINNValidationFiveOnlyZerosError

    return value


def validate_payee_inn(
    _type: PaymentType,
    value: str,
) -> str:
    if _type.fl:
        if value == '':
            return ''
        if len(value) != 12:
            raise PayeeINNValidationFLenError
    # TODO: add flow
