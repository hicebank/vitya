import re
from datetime import date
from typing import Any, Dict, List, Optional

from _decimal import Decimal

from vitya.payment_order.enums import PaymentType
from vitya.payment_order.errors import (
    CBCValidationEmptyNotAllowed,
    CBCValidationValueCannotZerosStarts,
    CBCValidationValueDigitsOnlyError,
    CBCValidationValueLenError,
    INNValidationLenError,
    KPPValidationValueCannotZerosStarts,
    KPPValidationValueDigitsOnlyError,
    KPPValidationValueLenError,
    NumberValidationLenError,
    OKTMOValidationEmptyNotAllowed,
    OKTMOValidationFNSEmptyNotAllowed,
    OKTMOValidationValueLenError,
    OKTMOValidationZerosNotAllowed,
    OperationKindValidationBudgetValueError,
    OperationKindValidationValueError,
    PayeeAccountValidationFNSValueError,
    PayeeAccountValidationLenError,
    PayeeAccountValidationNonEmptyError,
    PayeeINNValidationControlSumError,
    PayeeINNValidationFLLenError,
    PayeeINNValidationIPLenError,
    PayeeINNValidationLELenError,
    PayeeKPPValidationEmptyNotAllowed,
    PayeeKPPValidationOnlyEmptyError,
    PayeeKPPValidationValueCannotZerosStarts,
    PayeeKPPValidationValueDigitsOnlyError,
    PayeeKPPValidationValueLenError,
    PayerINNValidationEmptyNotAllowedError,
    PayerINNValidationStartWithZerosError,
    PayerINNValidationTMSLen10Error,
    PayerINNValidationTMSLen12Error,
    PayerKPPValidationINN10EmptyNotAllowed,
    PayerKPPValidationINN12OnlyEmptyError,
    PayerKPPValidationOnlyEmptyError,
    PayerKPPValidationValueCannotZerosStarts,
    PayerKPPValidationValueDigitsOnlyError,
    PayerKPPValidationValueLenError,
    PayerStatusValidationNullNotAllowedError,
    PayerStatusValidationTMS05NotAllowedError,
    PayerStatusValidationValueError,
    PurposeCodeValidationFlError,
    PurposeCodeValidationNullError,
    PurposeValidationCharactersError,
    PurposeValidationIPNDSError,
    PurposeValidationMaxLenError,
    ReasonValidationEmptyNotAllowed,
    ReasonValidationFNSOnlyEmptyError,
    ReasonValidationValueError,
    ReasonValidationValueLenError,
    UINValidationBOLenError,
    UINValidationControlSumError,
    UINValidationDigitsOnlyError,
    UINValidationFNSNotValueZeroError,
    UINValidationFNSValueZeroError,
    UINValidationLenError,
    UINValidationOnlyZeroError,
    UINValidationValueZeroError,
)
from vitya.payment_order.fields import Payee, Payer, PaymentOrder
from vitya.payment_order.payments.helpers import (
    CHARS_FOR_PURPOSE,
    PAYER_STATUSES,
    REASONS,
    REPLACE_CHARS_FOR_SPACE,
)
from vitya.pydantic_fields import Bic


def validate_payment_data(
    _type: PaymentType,
    *,
    name: str,
    form: str,
    number: str,
    creation_date: date,
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
    for_third_face: bool = False,
) -> Dict[str, Any]:
    number = validate_number(value=number)

    payee_account = validate_payee_account(_type=_type, value=payee_account)
    operation_kind = validate_operation_kind(_type=_type, value=operation_kind)
    purpose_code = validate_purpose_code(_type=_type, value=purpose_code)

    payer_status = validate_payer_status(  # type: ignore
        _type=_type,
        for_third_face=for_third_face,
        value=payer_status,
    )
    payer_inn = validate_payer_inn(
        _type=_type,
        payer_status=payer_status,
        value=payer_inn,
        for_third_face=for_third_face,
    )
    payee_inn = validate_payee_inn(
        _type=_type,
        value=payee_inn,
    )
    uin = validate_uin(_type=_type, value=uin, payer_status=payer_status, payer_inn=payer_inn)
    purpose = validate_purpose(_type=_type, value=purpose)

    payer_kpp = validate_payer_kpp(_type=_type, payer_inn=payer_inn, value=payer_kpp)
    payee_kpp = validate_payee_kpp(_type=_type, value=payee_kpp)
    cbc = validate_cbc(_type=_type, value=cbc)
    oktmo = validate_oktmo(value=oktmo, _type=_type, payer_status=payer_status)
    reason = validate_reason(_type=_type, value=reason)

    return {
        '_type': _type,
        'name': name,
        'form': form,
        'number': number,
        'creation_date': creation_date,
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


def validate_payee_account(
    value: str,
    _type: PaymentType,
) -> str:
    if value is None:
        raise PayeeAccountValidationNonEmptyError
    if len(value) != 20:
        raise PayeeAccountValidationLenError
    if _type == PaymentType.fns:
        if value != '03100643000000018500':
            raise PayeeAccountValidationFNSValueError
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
    value: Optional[str],
) -> str:
    value = value or '0'
    if len(value) > 210:
        raise PurposeValidationMaxLenError
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
    for_third_face: bool = False,
) -> str:
    if not _type.is_budget:
        if _type == PaymentType.le:
            validate_le_inn(value)
        else:
            validate_ip_and_fl_inn(value)
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
        if payer_status == '06' and for_third_face and len(value) != 10:
            raise PayerINNValidationTMSLen10Error

        if payer_status in {'16', '17'} and len(value) != 12:
            raise PayerINNValidationTMSLen12Error

    if value.startswith('00'):
        raise PayerINNValidationStartWithZerosError

    return value


def _count_inn_checksum(inn: str, coefficients: List[int]) -> int:
    assert len(inn) == len(coefficients)
    n = sum([int(digit) * coef for digit, coef in zip(inn, coefficients)])
    return n % 11 % 10


def validate_ip_and_fl_inn(inn: str) -> None:
    if not inn.isdigit():
        raise UINValidationDigitsOnlyError

    coefs10 = [2, 4, 10, 3, 5, 9, 4, 6, 8]
    coefs11 = [7] + coefs10
    coefs12 = [3] + coefs11
    n11 = _count_inn_checksum(inn[:10], coefs11)
    if n11 != int(inn[10]):
        raise PayeeINNValidationControlSumError

    n12 = _count_inn_checksum(inn[:11], coefs12)
    if n12 != int(inn[11]):
        raise PayeeINNValidationControlSumError
    return


def validate_le_inn(inn: str) -> None:
    if not inn.isdigit():
        raise UINValidationDigitsOnlyError

    coefs10 = [2, 4, 10, 3, 5, 9, 4, 6, 8]
    n10 = _count_inn_checksum(inn[:9], coefs10)
    if n10 != int(inn[9]):
        raise PayeeINNValidationControlSumError
    return


def validate_payee_inn(
    value: str,
    _type: PaymentType,
) -> str:
    value = value or '0'
    if _type == PaymentType.ip:
        if len(value) != 12:
            raise PayeeINNValidationIPLenError
        validate_ip_and_fl_inn(value)
        return value
    elif _type == PaymentType.fl:
        if value != '0' and len(value) != 12:
            raise PayeeINNValidationFLLenError
        elif value == '0':
            return value
        validate_ip_and_fl_inn(value)
        return value
    if len(value) != 10:
        raise PayeeINNValidationLELenError
    validate_le_inn(value)
    return value


def validate_payer_status(
    value: str,
    _type: PaymentType,
    for_third_face: bool,
) -> Optional[str]:
    is_empty = value is None or value in {'', '0'}
    if not _type.is_budget:
        return None

    if is_empty:
        raise PayerStatusValidationNullNotAllowedError

    if _type == PaymentType.tms and for_third_face and value == '06':
        raise PayerStatusValidationTMS05NotAllowedError

    if value not in PAYER_STATUSES:
        raise PayerStatusValidationValueError
    return value


def _validate_kpp(value: str) -> None:
    if len(value) != 9:
        raise KPPValidationValueLenError
    if not value.isdigit():
        raise KPPValidationValueDigitsOnlyError
    if value.startswith('00'):
        raise KPPValidationValueCannotZerosStarts


def validate_payer_kpp(
    value: str,
    _type: PaymentType,
    payer_inn: str,
) -> str:
    is_empty = value in {'', '0'}
    if not _type.is_budget:
        if not is_empty:
            raise PayerKPPValidationOnlyEmptyError
        return '0'

    if len(payer_inn) == 10 and is_empty:
        raise PayerKPPValidationINN10EmptyNotAllowed
    elif len(payer_inn) == 12 and not is_empty:
        raise PayerKPPValidationINN12OnlyEmptyError

    if not is_empty:
        try:
            _validate_kpp(value)
        except KPPValidationValueLenError as e:
            raise PayerKPPValidationValueLenError from e
        except KPPValidationValueDigitsOnlyError as e:
            raise PayerKPPValidationValueDigitsOnlyError from e
        except KPPValidationValueCannotZerosStarts as e:
            raise PayerKPPValidationValueCannotZerosStarts from e
    return value


def validate_payee_kpp(
    value: str,
    _type: PaymentType,
) -> str:
    is_empty = value in {'', '0'}
    if _type in {PaymentType.fl, PaymentType.ip}:
        if not is_empty:
            raise PayeeKPPValidationOnlyEmptyError
        return '0'

    if is_empty:
        raise PayeeKPPValidationEmptyNotAllowed

    try:
        _validate_kpp(value)
    except KPPValidationValueLenError as e:
        raise PayeeKPPValidationValueLenError from e
    except KPPValidationValueDigitsOnlyError as e:
        raise PayeeKPPValidationValueDigitsOnlyError from e
    except KPPValidationValueCannotZerosStarts as e:
        raise PayeeKPPValidationValueCannotZerosStarts from e
    return value


def validate_cbc(
    value: Optional[str],
    _type: PaymentType,
) -> Optional[str]:
    is_empty = value is None or value in {'', '0'}
    if not _type.is_budget:
        return None

    if _type == PaymentType.bo:
        if is_empty:
            return None

    if _type in {PaymentType.fns, PaymentType.tms} and is_empty:
        raise CBCValidationEmptyNotAllowed

    if not is_empty:
        assert value is not None
        if len(value) != 20:
            raise CBCValidationValueLenError
        if not value.isdigit():
            raise CBCValidationValueDigitsOnlyError
        if value.startswith('00'):
            raise CBCValidationValueCannotZerosStarts
    return value


def validate_oktmo(
    value: Optional[str],
    _type: PaymentType,
    payer_status: Optional[str],
) -> Optional[str]:
    is_empty = value is None or value in {'', '0'}
    if not _type.is_budget:
        return None

    if _type == PaymentType.fns and payer_status in {'01', '13'} and is_empty:
        return value
    if _type in {PaymentType.tms, PaymentType.bo} and is_empty:
        return value

    if value is None:
        raise OKTMOValidationEmptyNotAllowed

    if not (len(value) == 8 or len(value) == 11):
        raise OKTMOValidationValueLenError

    if all(c == '0' for c in value):
        raise OKTMOValidationZerosNotAllowed
    return value


def validate_reason(
    value: Optional[str],
    _type: PaymentType,
) -> Optional[str]:
    is_empty = value is None or value in {'', '0'}
    if not _type.is_budget:
        return None

    if _type in {PaymentType.tms, PaymentType.bo} and is_empty:
        return value

    if _type == PaymentType.fns:
        if not is_empty:
            raise ReasonValidationFNSOnlyEmptyError
        return '0'

    if value is None:
        raise ReasonValidationEmptyNotAllowed
    if len(value) != 2:
        raise ReasonValidationValueLenError
    if value not in REASONS:
        raise ReasonValidationValueError
    return value
