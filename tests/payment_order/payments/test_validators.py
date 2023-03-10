from typing import Optional, Type

import pytest

from vitya.payment_order.enums import PaymentType
from vitya.payment_order.errors import (
    INNValidationLenError,
    NumberValidationLenError,
    OperationKindValidationBudgetValueError,
    OperationKindValidationValueError,
    PayeeAccountValidationFNSValueError,
    PayeeAccountValidationLenError,
    PayeeAccountValidationNonEmptyError,
    PayerINNValidationEmptyNotAllowedError,
    PayerINNValidationFiveOnlyZerosError,
    PayerINNValidationStartWithZerosError,
    PayerINNValidationTMSLen10Error,
    PayerINNValidationTMSLen12Error,
    PurposeCodeValidationFlError,
    PurposeCodeValidationNullError,
    PurposeValidationCharactersError,
    PurposeValidationIPNDSError,
    PurposeValidationMaxLenError,
    UINValidationBOLenError,
    UINValidationControlSumError,
    UINValidationDigitsOnlyError,
    UINValidationFNSNotValueZeroError,
    UINValidationFNSValueZeroError,
    UINValidationLenError,
    UINValidationValueZeroError,
)
from vitya.payment_order.payments.validators import (
    validate_number,
    validate_operation_kind,
    validate_payee_account,
    validate_payer_inn,
    validate_purpose,
    validate_purpose_code,
    validate_uin,
)

VALID_UIN = '18209965144380684245'
INVALID_UIN = '18209965144380684246'
INN = '773605950159'


@pytest.mark.parametrize(
    'value, exception, expected_value',
    [
        (
            '000001',
            None,
            '000001',
        ),
        (
            '0000011',
            NumberValidationLenError,
            None,
        ),
    ]
)
def test_validate_number(
    value: str,
    exception: Optional[Type[Exception]],
    expected_value: str
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_number(value=value)
    else:
        assert validate_number(value=value) == expected_value


@pytest.mark.parametrize(
    'value, _type, exception, expected_value',
    [
        (
            '40802810722200035222',
            PaymentType.ip,
            None,
            '40802810722200035222',
        ),
        (
            None,
            PaymentType.ip,
            PayeeAccountValidationNonEmptyError,
            None,
        ),
        (
            '4080281072220003522',
            PaymentType.ip,
            PayeeAccountValidationLenError,
            None,
        ),
        (
            '03100643000000018500',
            PaymentType.fns,
            None,
            '03100643000000018500',
        ),
        (
            '03100643000000018501',
            PaymentType.fns,
            PayeeAccountValidationFNSValueError,
            None,
        ),
    ]
)
def test_validate_payee_account(
    value: str,
    _type: PaymentType,
    exception: Optional[Type[Exception]],
    expected_value: str
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_payee_account(value=value, _type=_type)
    else:
        assert validate_payee_account(value=value, _type=_type) == expected_value


@pytest.mark.parametrize(
    'value, _type, exception, expected_value',
    [
        (
            '02',
            PaymentType.ip,
            None,
            '02',
        ),
        (
            '02',
            PaymentType.bo,
            None,
            '02',
        ),
        (
            '03',
            PaymentType.bo,
            OperationKindValidationBudgetValueError,
            None,
        ),
        (
            '031',
            PaymentType.fl,
            OperationKindValidationValueError,
            None,
        ),
    ]
)
def test_validate_operation_kind(
    value: str,
    _type: PaymentType,
    exception: Optional[Type[Exception]],
    expected_value: str
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_operation_kind(value=value, _type=_type)
    else:
        assert validate_operation_kind(value=value, _type=_type) == expected_value


@pytest.mark.parametrize(
    'value, _type, exception, expected_value',
    [
        (
            1,
            PaymentType.fl,
            None,
            1,
        ),
        (
            6,
            PaymentType.fl,
            PurposeCodeValidationFlError,
            None,
        ),
        (
            None,
            PaymentType.ip,
            None,
            None,
        ),
        (
            1,
            PaymentType.ip,
            PurposeCodeValidationNullError,
            None,
        ),
    ]
)
def test_validate_purpose_code(
    value: int,
    _type: PaymentType,
    exception: Optional[Type[Exception]],
    expected_value: int
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_purpose_code(value=value, _type=_type)
    else:
        assert validate_purpose_code(value=value, _type=_type) == expected_value


@pytest.mark.parametrize(
    'value, _type, payer_status, payer_inn, exception, expected_value',
    [
        (
            '0',
            PaymentType.fl,
            '',
            '',
            None,
            '0',
        ),
        (
            None,
            PaymentType.fl,
            '',
            '',
            None,
            '0',
        ),
        (
            'a',
            PaymentType.fl,
            '',
            '',
            UINValidationDigitsOnlyError,
            None,
        ),
        (
            '0',
            PaymentType.fns,
            '31',
            '',
            UINValidationValueZeroError,
            None,
        ),
        (
            '0',
            PaymentType.bo,
            '',
            '',
            UINValidationBOLenError,
            None,
        ),
        (
            VALID_UIN,
            PaymentType.bo,
            '',
            '',
            None,
            VALID_UIN,
        ),
        # invalid uin control sum
        (
            INVALID_UIN,
            PaymentType.bo,
            '',
            '',
            UINValidationControlSumError,
            None,
        ),
        (
            None,
            PaymentType.fns,
            '13',
            '',
            UINValidationFNSValueZeroError,
            None,
        ),
        (
            VALID_UIN,
            PaymentType.fns,
            '13',
            '',
            None,
            VALID_UIN,
        ),
        (
            VALID_UIN,
            PaymentType.fns,
            '02',
            '',
            UINValidationFNSNotValueZeroError,
            None,
        ),
        (
            '0',
            PaymentType.fns,
            '02',
            '',
            None,
            '0',
        ),
        (
            '0',
            PaymentType.fns,
            '02',
            '',
            None,
            '0',
        ),
        (
            VALID_UIN + '1',
            PaymentType.fns,
            '',
            '',
            UINValidationLenError,
            None,
        ),
    ]
)
def test_validate_uin(
    value: Optional[str],
    _type: PaymentType,
    payer_status: str,
    payer_inn: str,
    exception: Optional[Type[Exception]],
    expected_value: str
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_uin(_type=_type, payer_inn=payer_inn, payer_status=payer_status, value=value)
    else:
        assert validate_uin(_type=_type, payer_inn=payer_inn, payer_status=payer_status, value=value) == expected_value


@pytest.mark.parametrize(
    'value, _type, exception, expected_value',
    [
        (
            '',
            PaymentType.fns,
            None,
            '0',
        ),
        (
            '1' * 211,
            PaymentType.fns,
            PurposeValidationMaxLenError,
            None,
        ),
        (
            '的',
            PaymentType.fns,
            PurposeValidationCharactersError,
            None,
        ),
        (
            'some',
            PaymentType.ip,
            PurposeValidationIPNDSError,
            None,
        ),
        (
            'some with НДС',
            PaymentType.ip,
            None,
            'some with НДС',
        ),
    ]
)
def test_validate_purpose(
    value: Optional[str],
    _type: PaymentType,
    exception: Optional[Type[Exception]],
    expected_value: str
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_purpose(_type=_type, value=value)
    else:
        assert validate_purpose(_type=_type, value=value) == expected_value


@pytest.mark.parametrize(
    'value, _type, payer_status, exception, expected_value',
    [
        (
            INN,
            PaymentType.fl,
            '',
            None,
            INN,
        ),
        (
            'a',
            PaymentType.fl,
            '',
            UINValidationDigitsOnlyError,
            None,
        ),
        (
            '',
            PaymentType.bo,
            '',
            None,
            '',
        ),
        (
            '',
            PaymentType.fns,
            '13',
            None,
            '',
        ),
        (
            '',
            PaymentType.tms,
            '30',
            None,
            '',
        ),
        (
            '',
            PaymentType.tms,
            '',
            PayerINNValidationEmptyNotAllowedError,
            None,
        ),
        (
            '5',
            PaymentType.tms,
            '',
            INNValidationLenError,
            None,
        ),
        (
            '12345',
            PaymentType.tms,
            '06',
            PayerINNValidationTMSLen10Error,
            None,
        ),
        (
            '12345',
            PaymentType.tms,
            '16',
            PayerINNValidationTMSLen12Error,
            None,
        ),
        (
            '00123',
            PaymentType.tms,
            '',
            PayerINNValidationStartWithZerosError,
            None,
        ),
        (
            INN,
            PaymentType.tms,
            '',
            None,
            INN,
        ),
    ]
)
def test_validate_payer_inn(
    value: Optional[str],
    _type: PaymentType,
    payer_status: str,
    exception: Optional[Type[Exception]],
    expected_value: str
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_payer_inn(_type=_type, payer_status=payer_status, value=value)
    else:
        assert expected_value == validate_payer_inn(_type=_type, payer_status=payer_status, value=value)
