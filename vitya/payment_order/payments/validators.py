from _decimal import Decimal
from datetime import date
from typing import Any, Optional

from vitya.payment_order.enums import PaymentType
from vitya.payment_order.errors import (
    OperationKindValidationBudgetValueError, OperationKindValidationValueError, PurposeCodeValidationFlError,
    PurposeCodeValidationNullError,
    UINValidationBOLenError, UINValidationBOValueError, UINValidationFNSValueZeroError, UINValidationValueZeroError,
)
from vitya.payment_order.fields import Payee, Payer, PaymentOrder
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
    pass


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


def validate_uin(
    _type: PaymentType,
    value: Optional[str],
    payee_account: str,
    payer_status: str,
    payer_inn: str,
) -> str:
    value = value or '0'
    len_value = len(value)
    if not _type.is_budget:
        return '0'

    if payer_status == '31' and value == '0':
        raise UINValidationValueZeroError

    if _type == PaymentType.bo:
        if not (len_value == 4 or len_value == 20 or len_value == 25):
            raise UINValidationBOLenError
        if payee_account.startswith(('03212', '03222', '03232', '03242', '03252', '03262', '03272')):
            if value == '0':
                raise UINValidationBOValueError

    if _type == PaymentType.fns and payer_status == '13' and payer_inn == '' and value == '0':
        raise UINValidationFNSValueZeroError
