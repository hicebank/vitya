import re
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional, Union

from vitya.errors import (
    PayerKPPValidationValueCannotZerosStarts,
    PayerKPPValidationValueDigitsOnlyError,
    ReceiverKPPValidationValueCannotZerosStarts,
    ReceiverKPPValidationValueDigitsOnlyError,
)
from vitya.payment_order.errors import (
    AccountNumberValidationDigitsOnlyError,
    AccountNumberValidationSizeError,
    AccountNumberValidationTypeError,
    AmountNotANumber,
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
    PayerStatusValidationTypeError,
    PayerStatusValidationValueError,
    PayerValidationSizeError,
    PaymentOrderLenError,
    PaymentOrderValidationError,
    PurposeCodeValidationTypeError,
    PurposeValidationMaxLenError,
    PurposeValidationTypeError,
    ReasonValidationTypeError,
    ReasonValidationValueLenError,
    ReceiverAccountNumberValidationDigitsOnlyError,
    ReceiverAccountNumberValidationSizeError,
    ReceiverAccountNumberValidationTypeError,
    ReceiverValidationNameError,
    ReceiverValidationSizeError,
    TaxPeriodValidationTypeError,
    TypeOfIncomeValidationError,
    TypeOfIncomeValidationTypeError,
    UINValidationControlSumError,
    UINValidationDigitsOnlyError,
    UINValidationLenError,
    UINValidationOnlyZeroError,
    UINValidationTypeError,
)
from vitya.payment_order.payments.constants import (
    CHANGE_YEAR,
    CHARS_FOR_PURPOSE,
    PAYER_STATUSES,
    PAYER_STATUSES_AFTER_2024,
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

    try:
        value = Decimal(amount)
    except InvalidOperation:
        raise AmountNotANumber
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


def validate_receiver(value: str) -> str:
    try:
        validate_customer(value)
    except CustomerValidationSizeError as e:
        raise ReceiverValidationSizeError from e
    if bool(re.match('(.*)(4)[0-9]{19}', value)):
        raise ReceiverValidationNameError
    return value


def validate_payment_order(value: Optional[Union[int, str]]) -> int:
    if value is None or value == '':
        return 5

    if isinstance(value, str) and len(value) != 1:
        raise PaymentOrderLenError
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


def validate_receiver_account_number(value: str) -> str:
    try:
        return validate_account_number(value)
    except AccountNumberValidationTypeError:
        raise ReceiverAccountNumberValidationTypeError
    except AccountNumberValidationSizeError:
        raise ReceiverAccountNumberValidationSizeError
    except AccountNumberValidationDigitsOnlyError:
        raise ReceiverAccountNumberValidationDigitsOnlyError


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


_PURPOSE_TRANS_TABLE = str.maketrans({char: ' ' for char in REPLACE_CHARS_FOR_SPACE})


def validate_purpose(value: str) -> Optional[str]:
    if not isinstance(value, str):
        raise PurposeValidationTypeError

    if value == '':
        return None

    value = ''.join(c for c in value.translate(_PURPOSE_TRANS_TABLE) if c in CHARS_FOR_PURPOSE)
    if len(value) > 210:
        raise PurposeValidationMaxLenError
    return value


def validate_payer_status(value: str) -> str:
    if not isinstance(value, str):
        raise PayerStatusValidationTypeError
    elif value not in (PAYER_STATUSES if date.today().year < CHANGE_YEAR else PAYER_STATUSES_AFTER_2024):
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


def validate_type_of_income(value: str) -> Optional[str]:
    if value in {'', None}:
        return None
    elif not isinstance(value, str):
        raise TypeOfIncomeValidationTypeError
    elif value not in {'1', '2', '3', '4', '5'}:
        raise TypeOfIncomeValidationError
    return value


def validate_payer_kpp(value: str) -> Optional[str]:
    if value in {'0', '', None}:
        return None

    if value.startswith('00'):
        raise PayerKPPValidationValueCannotZerosStarts
    if not value.isnumeric():
        raise PayerKPPValidationValueDigitsOnlyError

    return value


def validate_receiver_kpp(value: str) -> Optional[str]:
    if value in {'0', '', None}:
        return None

    if value.startswith('00'):
        raise ReceiverKPPValidationValueCannotZerosStarts
    if not value.isnumeric():
        raise ReceiverKPPValidationValueDigitsOnlyError

    return value
