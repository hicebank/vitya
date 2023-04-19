import re
from decimal import Decimal
from typing import Optional

from vitya.payment_order.errors import (
    AccountNumberValidationDigitsOnlyError,
    AccountNumberValidationSizeError,
    AccountNumberValidationTypeError,
    AmountValidationLengthError,
    AmountValidationLessOrEqualZeroError,
    CBCValidationTypeError,
    CBCValidationValueCannotZerosOnly,
    CBCValidationValueDigitsOnlyError,
    CBCValidationValueLenError,
    CustomerValidationSizeError,
    DocumentDateValidationTypeError,
    DocumentNumberValidationTypeError,
    NumberValidationLenError,
    OperationKindValidationTypeError,
    OperationKindValidationValueError,
    PayeeValidationNameError,
    PayeeValidationSizeError,
    PayerStatusValidationTypeError,
    PayerStatusValidationValueError,
    PayerValidationSizeError,
    PaymentOrderValidationError,
    PurposeCodeValidationTypeError,
    PurposeValidationCharactersError,
    PurposeValidationMaxLenError,
    PurposeValidationTypeError,
    ReasonValidationTypeError,
    ReasonValidationValueLenError,
    TaxPeriodValidationTypeError,
    UINValidationControlSumError,
    UINValidationDigitsOnlyError,
    UINValidationLenError,
    UINValidationOnlyZeroError,
    UINValidationTypeError,
)
from vitya.payment_order.payments.constants import (
    CHARS_FOR_PURPOSE,
    PAYER_STATUSES,
    REPLACE_CHARS_FOR_SPACE,
)


def validate_number(
    value: str,
) -> str:
    if len(value) > 6:
        raise NumberValidationLenError
    return value


def validate_amount(amount: str) -> Decimal:
    if isinstance(amount, str):
        if len(amount) > 18:
            raise AmountValidationLengthError

    value = Decimal(amount)
    if value <= Decimal(0.0):
        raise AmountValidationLessOrEqualZeroError

    return value


def validate_customer(value: str) -> str:
    len_value = len(value)
    if len_value < 1 or len_value > 160:
        raise CustomerValidationSizeError
    return value


def validate_payer(value: str) -> str:
    try:
        validate_customer(value)
    except CustomerValidationSizeError as e:
        raise PayerValidationSizeError from e
    return value


def validate_payee(value: str) -> str:
    try:
        validate_customer(value)
    except CustomerValidationSizeError as e:
        raise PayeeValidationSizeError from e
    if bool(re.match('(.*)(4)[0-9]{19}', value)):
        raise PayeeValidationNameError
    return value


def validate_payment_order(value: Optional[str]) -> int:
    if value is None or value == '':
        return 5

    try:
        value_int = int(value)
    except ValueError:
        raise PaymentOrderValidationError
    if value_int not in {1, 2, 3, 4, 5}:
        raise PaymentOrderValidationError
    return value_int


def validate_account_number(value: str) -> str:
    if not isinstance(value, str):
        raise AccountNumberValidationTypeError
    if len(value) != 20:
        raise AccountNumberValidationSizeError
    if not only_digits(value):
        raise AccountNumberValidationDigitsOnlyError
    return value


def validate_operation_kind(value: str) -> str:
    if not isinstance(value, str):
        raise OperationKindValidationTypeError
    if len(value) != 2:
        raise OperationKindValidationValueError
    return value


def validate_uin_control_sum(
    value: str
) -> None:
    if not only_digits(value):
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
        return

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


def validate_uin(value: str) -> Optional[str]:
    if not isinstance(value, str):
        raise UINValidationTypeError
    if value in {'', '0'}:
        return None
    if not (len(value) == 4 or len(value) == 20 or len(value) == 25):
        raise UINValidationLenError
    if len(value) == 4 and value == '0000':
        raise UINValidationOnlyZeroError
    validate_uin_control_sum(value)
    return value


def only_digits(value: str) -> bool:
    return re.match(r'^[0-9]+$', value) is not None


def validate_purpose_code(value: int) -> int:
    try:
        value = int(value)
    except Exception:
        raise PurposeCodeValidationTypeError
    return value


def validate_purpose(value: str) -> str:
    if not isinstance(value, str):
        raise PurposeValidationTypeError

    if value == '':
        return '0'

    if len(value) > 210:
        raise PurposeValidationMaxLenError

    replaced_space_value = ''.join(map(lambda x: x if x not in REPLACE_CHARS_FOR_SPACE else ' ', value))
    for c in replaced_space_value:
        if c not in CHARS_FOR_PURPOSE:
            raise PurposeValidationCharactersError
    return value


def validate_payer_status(value: str) -> str:
    if not isinstance(value, str):
        raise PayerStatusValidationTypeError
    elif value not in PAYER_STATUSES:
        raise PayerStatusValidationValueError
    return value


def validate_cbc(value: str) -> Optional[str]:
    if not isinstance(value, str):
        raise CBCValidationTypeError
    if value in {'', '0'}:
        return None
    if len(value) != 20:
        raise CBCValidationValueLenError
    elif not only_digits(value):
        raise CBCValidationValueDigitsOnlyError
    if all(c == '0' for c in value):
        raise CBCValidationValueCannotZerosOnly
    return value


def validate_reason(value: str) -> Optional[str]:
    if not isinstance(value, str):
        raise ReasonValidationTypeError
    elif value in {'', '0'}:
        return None
    elif len(value) != 2:
        raise ReasonValidationValueLenError
    return value


def validate_tax_period(value: str) -> Optional[str]:
    if not isinstance(value, str):
        raise TaxPeriodValidationTypeError
    elif value in {'', '0'}:
        return None
    return value


def validate_document_number(value: str) -> Optional[str]:
    if not isinstance(value, str):
        raise DocumentNumberValidationTypeError
    elif value in {'', '0'}:
        return None
    return value


def validate_document_date(value: str) -> Optional[str]:
    if not isinstance(value, str):
        raise DocumentDateValidationTypeError
    elif value in {'', '0'}:
        return None
    return value
