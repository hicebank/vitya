import re
from typing import List, Optional

from vitya.payment_order.enums import PaymentType
from vitya.payment_order.errors import (
    AccountValidationBICValueError,
    INNValidationControlSumError,
    INNValidationDigitsOnlyError,
    INNValidationLenError,
    OperationKindValidationBudgetValueError,
    PayeeAccountValidationBICValueError,
    PayeeAccountValidationFNSValueError,
    PayerINNValidationEmptyNotAllowedError,
    PayerINNValidationStartWithZerosError,
    PayerINNValidationTMSLen10Error,
    PayerINNValidationTMSLen12Error,
    PurposeCodeValidationFlError,
    PurposeCodeValidationNullError,
    PurposeValidationCharactersError,
    PurposeValidationIPNDSError,
    PurposeValidationMaxLenError,
    UINValidationFNSNotValueZeroError,
    UINValidationFNSValueZeroError,
    UINValidationValueZeroError,
)
from vitya.payment_order.fields import UIN, AccountNumber, OperationKind, PayerStatus
from vitya.payment_order.payments.helpers import (
    CHARS_FOR_PURPOSE,
    FNS_PAYEE_ACCOUNT_NUMBER,
    REPLACE_CHARS_FOR_SPACE,
)
from vitya.pydantic_fields import Bic, Inn


def replace_zero_to_none(value: Optional[str]) -> Optional[str]:
    return None if value in {'', '0'} else value


def validate_account_by_bic(
    account_number: AccountNumber,
    bic: Bic,
) -> None:
    _sum = 0
    for c, v in zip(bic[-3:] + account_number, [7, 1, 3] * 8):
        _sum += int(c) * v
    if _sum % 10 != 0:
        raise AccountValidationBICValueError


def validate_payee_account(
    value: AccountNumber,
    payment_type: PaymentType,
    payee_bic: Bic,
) -> str:
    if payment_type == PaymentType.FNS:
        if value != FNS_PAYEE_ACCOUNT_NUMBER:
            raise PayeeAccountValidationFNSValueError
    elif not payment_type.is_budget:
        try:
            validate_account_by_bic(account_number=value, bic=payee_bic)
        except AccountValidationBICValueError as e:
            raise PayeeAccountValidationBICValueError from e
    return value


def validate_operation_kind(
    value: OperationKind,
    payment_type: PaymentType
) -> OperationKind:
    if payment_type.is_budget:
        if value not in {'01', '02', '06'}:
            raise OperationKindValidationBudgetValueError
    return value


def validate_purpose_code(
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


def validate_uin(
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


def validate_purpose(
    value: Optional[str],
    payment_type: PaymentType,
) -> Optional[str]:
    value = replace_zero_to_none(value=value)
    if value is None:
        return None

    if len(value) > 210:
        raise PurposeValidationMaxLenError

    replaced_space_value = ''.join(map(lambda x: x if x not in REPLACE_CHARS_FOR_SPACE else ' ', value))
    for c in replaced_space_value:
        if c not in CHARS_FOR_PURPOSE:
            raise PurposeValidationCharactersError

    if payment_type == PaymentType.IP:
        if not re.search(r'(?i)\bНДС\b', replaced_space_value):
            raise PurposeValidationIPNDSError
    return value


def count_inn_checksum(inn: str, coefficients: List[int]) -> int:
    assert len(inn) == len(coefficients)
    n = sum([int(digit) * coef for digit, coef in zip(inn, coefficients)])
    return n % 11 % 10


def validate_ip_and_fl_inn(inn: str) -> None:
    if not inn.isdigit():
        raise INNValidationDigitsOnlyError

    coefs10 = [2, 4, 10, 3, 5, 9, 4, 6, 8]
    coefs11 = [7] + coefs10
    coefs12 = [3] + coefs11
    n11 = count_inn_checksum(inn[:10], coefs11)
    if n11 != int(inn[10]):
        raise INNValidationControlSumError

    n12 = count_inn_checksum(inn[:11], coefs12)
    if n12 != int(inn[11]):
        raise INNValidationControlSumError


def validate_le_inn(inn: str) -> None:
    if not inn.isdigit():
        raise INNValidationDigitsOnlyError

    coefs10 = [2, 4, 10, 3, 5, 9, 4, 6, 8]
    n10 = count_inn_checksum(inn[:9], coefs10)
    if n10 != int(inn[9]):
        raise INNValidationControlSumError


def validate_inn_check_sum(value: str) -> None:
    if len(value) == 12:
        return validate_ip_and_fl_inn(inn=value)
    elif len(value) == 10:
        return validate_le_inn(inn=value)
    elif len(value) == 5:
        return
    raise INNValidationLenError


def validate_payer_inn(
    value: Optional[Inn],
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
            raise PayerINNValidationTMSLen10Error

        if payer_status in {'16', '17'} and len(value) != 12:
            raise PayerINNValidationTMSLen12Error

    if value.startswith('00'):
        raise PayerINNValidationStartWithZerosError

    return value
