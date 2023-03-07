from typing import Optional, Type

import pytest

from tests.payment_order.testdata import BIC, INN, INVALID_UIN, IP_ACCOUNT, VALID_UIN
from vitya.payment_order.enums import PaymentType
from vitya.payment_order.errors import (
    INNValidationDigitsOnlyError,
    INNValidationLenError,
    OperationKindValidationBudgetValueError,
    OperationKindValidationValueError,
    PayeeAccountValidationBICValueError,
    PayeeAccountValidationFNSValueError,
    PayeeAccountValidationLenError,
    PayeeAccountValidationNonEmptyError,
    PayerINNValidationEmptyNotAllowedError,
    PayerINNValidationStartWithZerosError,
    PayerINNValidationTMSLen10Error,
    PayerINNValidationTMSLen12Error,
    PurposeCodeValidationFlError,
    PurposeCodeValidationNullError,
    PurposeValidationCharactersError,
    PurposeValidationIPNDSError,
    PurposeValidationMaxLenError,
    UINValidationControlSumError,
    UINValidationFNSNotValueZeroError,
    UINValidationFNSValueZeroError,
    UINValidationLenError,
    UINValidationValueZeroError,
)
from vitya.payment_order.payments.validators import (
    validate_account_by_bic,
    validate_operation_kind,
    validate_payee_account,
    validate_payer_inn,
    validate_purpose,
    validate_purpose_code,
    validate_uin,
)
from vitya.pydantic_fields import Bic


@pytest.mark.parametrize(
    'value, _type, payee_bic, exception, expected_value',
    [
        (
            IP_ACCOUNT,
            PaymentType.IP,
            BIC,
            None,
            IP_ACCOUNT,
        ),
        (
            None,
            PaymentType.IP,
            '',
            PayeeAccountValidationNonEmptyError,
            None,
        ),
        (
            IP_ACCOUNT[:-1],
            PaymentType.IP,
            '',
            PayeeAccountValidationLenError,
            None,
        ),
        (
            '03100643000000018500',
            PaymentType.FNS,
            '',
            None,
            '03100643000000018500',
        ),
        (
            '03100643000000018501',
            PaymentType.FNS,
            '',
            PayeeAccountValidationFNSValueError,
            None,
        ),
    ]
)
def test_validate_payee_account(
    value: str,
    _type: PaymentType,
    payee_bic: Bic,
    exception: Optional[Type[Exception]],
    expected_value: str
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_payee_account(value=value, _type=_type, payee_bic=payee_bic)
    else:
        assert validate_payee_account(value=value, _type=_type, payee_bic=payee_bic) == expected_value


@pytest.mark.parametrize(
    'account_number, bic, exception',
    [
        (
            IP_ACCOUNT,
            BIC,
            None,
        ),
        (
            IP_ACCOUNT[:-1] + '0',
            BIC,
            PayeeAccountValidationBICValueError,
        ),
    ]
)
def test_validate_account_by_bic(
    account_number: str,
    bic: Bic,
    exception: Optional[Type[Exception]],
) -> None:
    if exception:
        with pytest.raises(Exception):
            validate_account_by_bic(account_number=account_number, bic=bic)
    else:
        validate_account_by_bic(account_number=account_number, bic=bic)


@pytest.mark.parametrize(
    'value, _type, exception, expected_value',
    [
        (
            '02',
            PaymentType.IP,
            None,
            '02',
        ),
        (
            '02',
            PaymentType.BUDGET_OTHER,
            None,
            '02',
        ),
        (
            '03',
            PaymentType.BUDGET_OTHER,
            OperationKindValidationBudgetValueError,
            None,
        ),
        (
            '031',
            PaymentType.FL,
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
            PaymentType.FL,
            None,
            1,
        ),
        (
            6,
            PaymentType.FL,
            PurposeCodeValidationFlError,
            None,
        ),
        (
            None,
            PaymentType.IP,
            None,
            None,
        ),
        (
            1,
            PaymentType.IP,
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
            '',
            PaymentType.FL,
            '',
            '',
            None,
            None,
        ),
        (
            None,
            PaymentType.FL,
            '',
            '',
            None,
            None,
        ),
        (
            None,
            PaymentType.FNS,
            '31',
            '',
            UINValidationValueZeroError,
            None,
        ),
        (
            '0',
            PaymentType.BUDGET_OTHER,
            '',
            '',
            None,
            None,
        ),
        (
            VALID_UIN,
            PaymentType.BUDGET_OTHER,
            '',
            '',
            None,
            VALID_UIN,
        ),
        # invalid uin control sum
        (
            INVALID_UIN,
            PaymentType.BUDGET_OTHER,
            '',
            '',
            UINValidationControlSumError,
            None,
        ),
        (
            None,
            PaymentType.FNS,
            '13',
            None,
            UINValidationFNSValueZeroError,
            None,
        ),
        (
            VALID_UIN,
            PaymentType.FNS,
            '13',
            '',
            None,
            VALID_UIN,
        ),
        (
            VALID_UIN,
            PaymentType.FNS,
            '02',
            '',
            UINValidationFNSNotValueZeroError,
            None,
        ),
        (
            '',
            PaymentType.FNS,
            '02',
            '',
            None,
            None,
        ),
        (
            None,
            PaymentType.FNS,
            '02',
            '',
            None,
            None,
        ),
        (
            VALID_UIN + '1',
            PaymentType.FNS,
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
            PaymentType.FNS,
            None,
            None,
        ),
        (
            None,
            PaymentType.FNS,
            None,
            None,
        ),
        (
            '1' * 211,
            PaymentType.FNS,
            PurposeValidationMaxLenError,
            None,
        ),
        (
            '的',
            PaymentType.FNS,
            PurposeValidationCharactersError,
            None,
        ),
        (
            'some',
            PaymentType.IP,
            PurposeValidationIPNDSError,
            None,
        ),
        (
            'some with НДС',
            PaymentType.IP,
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
    'value, _type, payer_status, for_third_face, exception, expected_value',
    [
        (
            INN,
            PaymentType.FL,
            '',
            False,
            None,
            INN,
        ),
        (
            'a',
            PaymentType.FL,
            '',
            False,
            INNValidationDigitsOnlyError,
            None,
        ),
        (
            None,
            PaymentType.BUDGET_OTHER,
            '',
            False,
            None,
            None,
        ),
        (
            None,
            PaymentType.FNS,
            '13',
            False,
            None,
            None,
        ),
        (
            None,
            PaymentType.CUSTOMS,
            '30',
            False,
            None,
            None,
        ),
        (
            '',
            PaymentType.CUSTOMS,
            '',
            False,
            PayerINNValidationEmptyNotAllowedError,
            None,
        ),
        (
            '5',
            PaymentType.CUSTOMS,
            '',
            False,
            INNValidationLenError,
            None,
        ),
        (
            '12345',
            PaymentType.CUSTOMS,
            '06',
            True,
            PayerINNValidationTMSLen10Error,
            None,
        ),
        (
            '12345',
            PaymentType.CUSTOMS,
            '16',
            False,
            PayerINNValidationTMSLen12Error,
            None,
        ),
        (
            '00123',
            PaymentType.CUSTOMS,
            '',
            False,
            PayerINNValidationStartWithZerosError,
            None,
        ),
        (
            '00000',
            PaymentType.CUSTOMS,
            '',
            False,
            PayerINNValidationStartWithZerosError,
            None,
        ),
        (
            INN,
            PaymentType.CUSTOMS,
            '',
            False,
            None,
            INN,
        ),
    ]
)
def test_validate_payer_inn(
    value: Optional[str],
    _type: PaymentType,
    payer_status: str,
    for_third_face: bool,
    exception: Optional[Type[Exception]],
    expected_value: str
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_payer_inn(_type=_type, payer_status=payer_status, value=value, for_third_face=for_third_face)
    else:
        assert expected_value == validate_payer_inn(
            _type=_type, payer_status=payer_status, value=value, for_third_face=for_third_face,
        )
