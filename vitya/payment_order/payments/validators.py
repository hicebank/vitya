import re
from typing import Optional

from vitya.payment_order.enums import PaymentType
from vitya.payment_order.errors import (
    AccountValidationBICValueError,
    OperationKindValidationBudgetValueError,
    PayeeAccountValidationBICValueError,
    PayeeAccountValidationFNSValueError,
    PayerINNValidationEmptyNotAllowedError,
    PayerINNValidationStartWithZerosError,
    PayerINNValidationTMSLen10Error,
    PayerINNValidationTMSLen12Error,
    PurposeCodeValidationFlError,
    PurposeCodeValidationNullError,
    PurposeValidationIPNDSError,
    UINValidationFNSNotValueZeroError,
    UINValidationFNSValueZeroError,
    UINValidationValueZeroError,
)
from vitya.payment_order.fields import (
    AccountNumber,
    OperationKind,
    PayerStatus,
    Purpose,
    Uin,
)
from vitya.payment_order.payments.helpers import FNS_PAYEE_ACCOUNT_NUMBER
from vitya.pydantic_fields import Bic, Inn


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
    value: Optional[Uin],
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
    value: Optional[Purpose],
    payment_type: PaymentType,
) -> Optional[str]:
    if value is None:
        return None

    if payment_type == PaymentType.IP:
        if not re.search(r'(?i)\bНДС\b', value):
            raise PurposeValidationIPNDSError
    return value


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
