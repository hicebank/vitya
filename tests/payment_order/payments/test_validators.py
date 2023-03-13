from typing import Optional, Type

import pytest

from vitya.payment_order.enums import PaymentType
from vitya.payment_order.errors import (
    CBCValidationEmptyNotAllowed,
    CBCValidationValueCannotZerosStarts,
    CBCValidationValueDigitsOnlyError,
    CBCValidationValueLenError,
    DocumentNumberValidationBOEmptyNotAllowed,
    DocumentNumberValidationBOOnlyEmptyError,
    DocumentNumberValidationBOValueError,
    DocumentNumberValidationBOValueLenError,
    DocumentNumberValidationFNSOnlyEmptyError,
    DocumentNumberValidationTMS00ValueError,
    DocumentNumberValidationTMSValueLen7Error,
    DocumentNumberValidationTMSValueLen15Error,
    INNValidationLenError,
    NumberValidationLenError,
    OKTMOValidationFNSEmptyNotAllowed,
    OKTMOValidationValueLenError,
    OKTMOValidationZerosNotAllowed,
    OperationKindValidationBudgetValueError,
    OperationKindValidationValueError,
    PayeeAccountValidationFNSValueError,
    PayeeAccountValidationLenError,
    PayeeAccountValidationNonEmptyError,
    PayeeINNValidationControlSumError,
    PayeeINNValidationIPLenError,
    PayeeINNValidationLELenError,
    PayeeKPPValidationEmptyNotAllowed,
    PayeeKPPValidationOnlyEmptyError,
    PayeeKPPValidationValueCannotZerosStarts,
    PayeeKPPValidationValueDigitsOnlyError,
    PayeeKPPValidationValueLenError,
    PayerINNValidationEmptyNotAllowedError,
    PayerINNValidationFiveOnlyZerosError,
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
    ReasonValidationValueError,
    ReasonValidationValueLenError,
    TaxPeriodValidationBOValueLenError,
    TaxPeriodValidationFNS01OnlyEmpty,
    TaxPeriodValidationFNS02EmptyNotAllowed,
    TaxPeriodValidationFNSEmptyNotAllowed,
    TaxPeriodValidationFNSValueLenError,
    TaxPeriodValidationTMSEmptyNotAllowed,
    TaxPeriodValidationTMSValueLenError,
    UINValidationBOLenError,
    UINValidationControlSumError,
    UINValidationDigitsOnlyError,
    UINValidationFNSNotValueZeroError,
    UINValidationFNSValueZeroError,
    UINValidationLenError,
    UINValidationValueZeroError,
)
from vitya.payment_order.payments.validators import (
    validate_cbc,
    validate_document_number,
    validate_number,
    validate_oktmo,
    validate_operation_kind,
    validate_payee_account,
    validate_payee_inn,
    validate_payee_kpp,
    validate_payer_inn,
    validate_payer_kpp,
    validate_payer_status,
    validate_purpose,
    validate_purpose_code,
    validate_reason,
    validate_tax_period,
    validate_uin,
)

VALID_UIN = '18209965144380684245'
INVALID_UIN = '18209965144380684246'
INN = '773605950159'

FL_INN = '848839660257'
INVALID_FL_INN = '848839660258'
IP_INN = '598092767948'
INVALID_IP_INN = '598092767949'
LE_INN = '1840493716'
INVALID_LE_INN = '1840493717'

KPP = '352643608'
CBC = '18201061201010000510'
OKTMO = '25600000'


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
    'value, _type, payer_status, for_third_face, exception, expected_value',
    [
        (
            INN,
            PaymentType.fl,
            '',
            False,
            None,
            INN,
        ),
        (
            'a',
            PaymentType.fl,
            '',
            False,
            UINValidationDigitsOnlyError,
            None,
        ),
        (
            '',
            PaymentType.bo,
            '',
            False,
            None,
            '',
        ),
        (
            '',
            PaymentType.fns,
            '13',
            False,
            None,
            '',
        ),
        (
            '',
            PaymentType.tms,
            '30',
            False,
            None,
            '',
        ),
        (
            '',
            PaymentType.tms,
            '',
            False,
            PayerINNValidationEmptyNotAllowedError,
            None,
        ),
        (
            '5',
            PaymentType.tms,
            '',
            False,
            INNValidationLenError,
            None,
        ),
        (
            '12345',
            PaymentType.tms,
            '06',
            True,
            PayerINNValidationTMSLen10Error,
            None,
        ),
        (
            '12345',
            PaymentType.tms,
            '16',
            False,
            PayerINNValidationTMSLen12Error,
            None,
        ),
        (
            '00123',
            PaymentType.tms,
            '',
            False,
            PayerINNValidationStartWithZerosError,
            None,
        ),
        (
            INN,
            PaymentType.tms,
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


@pytest.mark.parametrize(
    'value, _type, exception, expected_value',
    [
        (
            IP_INN,
            PaymentType.ip,
            None,
            IP_INN,
        ),
        (
            '1',
            PaymentType.ip,
            PayeeINNValidationIPLenError,
            None,
        ),
        (
            INVALID_IP_INN,
            PaymentType.ip,
            PayeeINNValidationControlSumError,
            None,
        ),
        (
            None,
            PaymentType.fl,
            None,
            '0',
        ),
        (
            '0',
            PaymentType.fl,
            None,
            '0',
        ),
        (
            FL_INN,
            PaymentType.fl,
            None,
            FL_INN,
        ),
        (
            INVALID_FL_INN,
            PaymentType.fl,
            PayeeINNValidationControlSumError,
            None,
        ),
        (
            INVALID_FL_INN,
            PaymentType.fl,
            PayeeINNValidationControlSumError,
            None,
        ),
        (
            LE_INN,
            PaymentType.bo,
            None,
            LE_INN,
        ),
        (
            '1',
            PaymentType.bo,
            PayeeINNValidationLELenError,
            None,
        ),
        (
            INVALID_LE_INN,
            PaymentType.bo,
            PayeeINNValidationControlSumError,
            None,
        ),
    ]
)
def test_validate_payee_inn(
    value: Optional[str],
    _type: PaymentType,
    exception: Optional[Type[Exception]],
    expected_value: str
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_payee_inn(_type=_type, value=value)
    else:
        assert expected_value == validate_payee_inn(_type=_type, value=value)


@pytest.mark.parametrize(
    'value, _type, for_third_face, exception, expected_value',
    [
        (
            None,
            PaymentType.fl,
            False,
            None,
            None,
        ),
        (
            None,
            PaymentType.fns,
            False,
            PayerStatusValidationNullNotAllowedError,
            None,
        ),
        (
            '06',
            PaymentType.tms,
            True,
            PayerStatusValidationTMS05NotAllowedError,
            None,
        ),
        (
            '99',
            PaymentType.fns,
            True,
            PayerStatusValidationValueError,
            None,
        ),
    ]
)
def test_validate_payer_status(
    value: Optional[str],
    _type: PaymentType,
    for_third_face: bool,
    exception: Optional[Type[Exception]],
    expected_value: str
):
    if exception:
        with pytest.raises(exception):
            validate_payer_status(_type=_type, value=value, for_third_face=for_third_face)
    else:
        assert expected_value == validate_payer_status(_type=_type, value=value, for_third_face=for_third_face)


@pytest.mark.parametrize(
    'value, _type, payer_inn, exception, expected_value',
    [
        (
            '',
            PaymentType.fl,
            INN,
            None,
            '0',
        ),
        (
            KPP,
            PaymentType.fl,
            INN,
            PayerKPPValidationOnlyEmptyError,
            None,
        ),
        (
            '',
            PaymentType.fns,
            LE_INN,
            PayerKPPValidationINN10EmptyNotAllowed,
            None,
        ),
        (
            KPP,
            PaymentType.fns,
            IP_INN,
            PayerKPPValidationINN12OnlyEmptyError,
            None,
        ),
        (
            '0123456780',
            PaymentType.fns,
            LE_INN,
            PayerKPPValidationValueLenError,
            None,
        ),
        (
            '01234567a',
            PaymentType.fns,
            LE_INN,
            PayerKPPValidationValueDigitsOnlyError,
            None,
        ),
        (
            KPP,
            PaymentType.fns,
            LE_INN,
            None,
            KPP,
        ),
        (
            '001234567',
            PaymentType.bo,
            LE_INN,
            PayerKPPValidationValueCannotZerosStarts,
            None,
        )
    ]
)
def test_validate_payer_kpp(
    value: str,
    _type: PaymentType,
    payer_inn: str,
    exception: Optional[Type[Exception]],
    expected_value: str
):
    if exception:
        with pytest.raises(exception):
            validate_payer_kpp(_type=_type, value=value, payer_inn=payer_inn)
    else:
        assert expected_value == validate_payer_kpp(_type=_type, value=value, payer_inn=payer_inn)


@pytest.mark.parametrize(
    'value, _type, exception, expected_value',
    [
        (
            '',
            PaymentType.fl,
            None,
            '0',
        ),
        (
            KPP,
            PaymentType.fl,
            PayeeKPPValidationOnlyEmptyError,
            None,
        ),
        (
            '0123456780',
            PaymentType.fns,
            PayeeKPPValidationValueLenError,
            None,
        ),
        (
            '01234567a',
            PaymentType.fns,
            PayeeKPPValidationValueDigitsOnlyError,
            None,
        ),
        (
            KPP,
            PaymentType.fns,
            None,
            KPP,
        ),
        (
            '',
            PaymentType.fns,
            PayeeKPPValidationEmptyNotAllowed,
            None
        ),
        (
            '001234567',
            PaymentType.bo,
            PayeeKPPValidationValueCannotZerosStarts,
            None,
        )
    ]
)
def test_validate_payee_kpp(
    value: str,
    _type: PaymentType,
    exception: Optional[Type[Exception]],
    expected_value: str
):
    if exception:
        with pytest.raises(exception):
            validate_payee_kpp(_type=_type, value=value)
    else:
        assert expected_value == validate_payee_kpp(_type=_type, value=value)


@pytest.mark.parametrize(
    'value, _type, exception, expected_value',
    [
        (
            '',
            PaymentType.fl,
            None,
            None,
        ),
        (
            '',
            PaymentType.bo,
            None,
            None,
        ),
        (
            '',
            PaymentType.fns,
            CBCValidationEmptyNotAllowed,
            None,
        ),
        (
            '',
            PaymentType.tms,
            CBCValidationEmptyNotAllowed,
            None,
        ),
        (
            '01',
            PaymentType.tms,
            CBCValidationValueLenError,
            None,
        ),
        (
            'a' * 20,
            PaymentType.tms,
            CBCValidationValueDigitsOnlyError,
            None,
        ),
        (
            '00' + '1' * 18,
            PaymentType.tms,
            CBCValidationValueCannotZerosStarts,
            None,
        ),
        (
            CBC,
            PaymentType.tms,
            None,
            CBC,
        )

    ]
)
def test_validate_cbc(
    value: str,
    _type: PaymentType,
    exception: Optional[Type[Exception]],
    expected_value: str
):
    if exception:
        with pytest.raises(exception):
            validate_cbc(_type=_type, value=value)
    else:
        assert expected_value == validate_cbc(_type=_type, value=value)


@pytest.mark.parametrize(
    'value, _type, payer_status, exception, expected_value',
    [
        (
            None,
            PaymentType.fl,
            None,
            None,
            None,
        ),
        (
            None,
            PaymentType.fns,
            '01',
            None,
            None,
        ),
        (
            None,
            PaymentType.fns,
            '13',
            None,
            None,
        ),
        (
            None,
            PaymentType.tms,
            None,
            None,
            None,
        ),
        (
            None,
            PaymentType.bo,
            None,
            None,
            None,
        ),
        (
            '0123456',
            PaymentType.fns,
            None,
            OKTMOValidationValueLenError,
            None,
        ),
        (
            '00000000',
            PaymentType.fns,
            None,
            OKTMOValidationZerosNotAllowed,
            None,
        ),
        (
            OKTMO,
            PaymentType.fns,
            None,
            None,
            OKTMO,
        )
    ]
)
def test_validate_oktmo(
    value: str,
    _type: PaymentType,
    payer_status: str,
    exception: Optional[Type[Exception]],
    expected_value: str
):
    if exception:
        with pytest.raises(exception):
            validate_oktmo(_type=_type, value=value, payer_status=payer_status)
    else:
        assert expected_value == validate_oktmo(_type=_type, value=value, payer_status=payer_status)


@pytest.mark.parametrize(
    'value, _type, exception, expected_value',
    [
        (
            None,
            PaymentType.fl,
            None,
            None,
        ),
        (
            None,
            PaymentType.bo,
            None,
            None,
        ),
        (
            None,
            PaymentType.tms,
            None,
            None,
        ),
        (
            '031',
            PaymentType.tms,
            ReasonValidationValueLenError,
            None,
        ),
        (
            'AD',
            PaymentType.tms,
            ReasonValidationValueError,
            None,
        ),
    ]
)
def test_validate_reason(
    value: str,
    _type: PaymentType,
    exception: Optional[Type[Exception]],
    expected_value: str
):
    if exception:
        with pytest.raises(exception):
            validate_reason(_type=_type, value=value)
    else:
        assert expected_value == validate_reason(_type=_type, value=value)


@pytest.mark.parametrize(
    'value, _type, payer_status, exception, expected_value',
    [
        (
            None,
            PaymentType.fl,
            None,
            None,
            None,
        ),
        (
            None,
            PaymentType.bo,
            None,
            None,
            '0',
        ),
        (
            '01',
            PaymentType.bo,
            None,
            TaxPeriodValidationBOValueLenError,
            None,
        ),
        (
            '0123456789',
            PaymentType.bo,
            None,
            None,
            '0123456789',
        ),
        (
            None,
            PaymentType.tms,
            None,
            TaxPeriodValidationTMSEmptyNotAllowed,
            None,
        ),
        (
            '1',
            PaymentType.tms,
            None,
            TaxPeriodValidationTMSValueLenError,
            None,
        ),
        (
            '01234567',
            PaymentType.tms,
            None,
            None,
            '01234567',
        ),
        (
            None,
            PaymentType.fns,
            '02',
            TaxPeriodValidationFNS02EmptyNotAllowed,
            None,
        ),
        (
            '1',
            PaymentType.fns,
            '13',
            TaxPeriodValidationFNS01OnlyEmpty,
            None,
        ),
        (
            '0',
            PaymentType.fns,
            '13',
            None,
            '0',
        ),
        (
            None,
            PaymentType.fns,
            None,
            TaxPeriodValidationFNSEmptyNotAllowed,
            None,
        ),
        (
            '12',
            PaymentType.fns,
            None,
            TaxPeriodValidationFNSValueLenError,
            None,
        ),
        (
            '0123456789',
            PaymentType.fns,
            None,
            None,
            '0123456789',
        ),
    ]
)
def test_validate_tax_period(
    value: str,
    _type: PaymentType,
    payer_status: Optional[str],
    exception: Optional[Type[Exception]],
    expected_value: str
):
    if exception:
        with pytest.raises(exception):
            validate_tax_period(_type=_type, value=value, payer_status=payer_status)
    else:
        assert expected_value == validate_tax_period(_type=_type, value=value, payer_status=payer_status)


@pytest.mark.parametrize(
    'value, _type, payer_status, payee_account, payer_inn, uin, '
    'reason, exception, expected_value',
    [
        (
            None,
            PaymentType.fl,
            None,
            '',
            '',
            '',
            '',
            None,
            None,
        ),
        (
            None,
            PaymentType.fns,
            None,
            '',
            '',
            '',
            '',
            None,
            '0',
        ),
        (
            '02',
            PaymentType.fns,
            None,
            '',
            '',
            '',
            '',
            DocumentNumberValidationFNSOnlyEmptyError,
            None,
        ),
        (
            '02',
            PaymentType.bo,
            '31',
            '03212',
            '',
            '1',
            '',
            DocumentNumberValidationBOOnlyEmptyError,
            None,
        ),
        (
            None,
            PaymentType.bo,
            '31',
            '03212',
            '',
            '1',
            '',
            None,
            '0',
        ),
        (
            None,
            PaymentType.bo,
            '24',
            '',
            None,
            None,
            '',
            DocumentNumberValidationBOEmptyNotAllowed,
            None,
        ),
        (
            '1' * 16,
            PaymentType.bo,
            '24',
            '',
            None,
            None,
            '',
            DocumentNumberValidationBOValueLenError,
            None,
        ),
        (
            '02',
            PaymentType.bo,
            '24',
            '',
            None,
            None,
            '',
            DocumentNumberValidationBOValueError,
            None,
        ),
        (
            '02;',
            PaymentType.bo,
            '24',
            '',
            None,
            None,
            '',
            None,
            '02;',
        ),
        (
            None,
            PaymentType.bo,
            '00',
            '',
            None,
            None,
            '',
            None,
            None,
        ),
        (
            None,
            PaymentType.tms,
            '',
            '',
            None,
            None,
            '00',
            DocumentNumberValidationTMS00ValueError,
            None,
        ),
        (
            '1',
            PaymentType.tms,
            '',
            '',
            None,
            None,
            '00',
            DocumentNumberValidationTMS00ValueError,
            None,
        ),
        (
            '1' * 8,
            PaymentType.tms,
            '',
            '',
            None,
            None,
            'ПК',
            DocumentNumberValidationTMSValueLen7Error,
            None,
        ),
        (
            '',
            PaymentType.tms,
            '',
            '',
            None,
            None,
            'ИЛ',
            DocumentNumberValidationTMSValueLen15Error,
            None,
        ),
        (
            '1' * 16,
            PaymentType.tms,
            '',
            '',
            None,
            None,
            'ИЛ',
            DocumentNumberValidationTMSValueLen15Error,
            None,
        ),
        (
            '02',
            PaymentType.tms,
            '',
            '',
            None,
            None,
            'ИЛ',
            None,
            '02',
        ),
    ]
)
def test_validate_document_number(
    value: str,
    _type: PaymentType,
    payer_status: Optional[str],
    payee_account: str,
    payer_inn: Optional[str],
    uin: Optional[str],
    reason: Optional[str],
    exception: Optional[Type[Exception]],
    expected_value: str
):
    if exception:
        with pytest.raises(exception):
            validate_document_number(
                value=value,
                _type=_type,
                payer_status=payer_status,
                payee_account=payee_account,
                payer_inn=payer_inn,
                uin=uin,
                reason=reason,
            )
    else:
        assert expected_value == validate_document_number(
            value=value,
            _type=_type,
            payer_status=payer_status,
            payee_account=payee_account,
            payer_inn=payer_inn,
            uin=uin,
            reason=reason,
        )
