from typing import Optional

import pytest
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from tests.payment_order.testdata import LE_INN
from vitya.error_description import AlertBody, AlertGenerator
from vitya.payment_order.enums import PaymentType
from vitya.payment_order.errors import (
    ReceiverAccountNumberValidationDigitsOnlyError,
    ReceiverAccountValidationBICValueError,
    ReceiverAccountValidationFNSValueError,
)
from vitya.payment_order.fields import (
    Amount,
    PayerAccountNumber,
    PayerINN,
    PayerKPP,
    PayerStatus,
    Receiver,
    ReceiverAccountNumber,
    ReceiverBIC,
    ReceiverKPP,
)
from vitya.payment_order.payments.checkers import BaseModelChecker, CheckerError


class Payment(BaseModelChecker):
    src_account: PayerAccountNumber  # [9]
    dst_account: ReceiverAccountNumber  # [17]
    amount: Amount  # [7]
    dst_name: Receiver  # [16]
    dst_bic: ReceiverBIC  # [14]
    dst_kpp: Optional[ReceiverKPP]  # [103]


ALERT_GENERATOR = AlertGenerator(
    {
        'amount': 'amount',
        'payer': 'dst_name',
        'receiver_bic': 'dst_bic',
        'receiver': 'dst_name',
        'receiver_account_number': 'dst_account',
    }
)


def test_alert_generator_not_none_field():
    try:
        Payment(
            src_account=PayerAccountNumber('40802810822200040036'),
            dst_account=ReceiverAccountNumber('40702810438000185552'),
            amount=None,
            dst_name=Receiver('Foo'),
            dst_bic=ReceiverBIC('044525225'),
        )
    except Exception as e:
        assert ALERT_GENERATOR.get_error_client_alerts(e) == [
            AlertBody(
                alert='Поле «Сумма» должно быть заполнено',
                failed_field='amount',
                failed_field_class_name='amount'
            )
        ]
    else:
        raise RuntimeError


def test_alert_generator_incorrect_len():
    try:
        Payment(
            src_account=PayerAccountNumber('40802810822200040036'),
            dst_account=ReceiverAccountNumber('40702810438000185552'),
            amount=Amount('1' * 20),
            dst_name=Receiver('Foo'),
            dst_bic=ReceiverBIC('044525225'),
        )
    except Exception as e:
        assert ALERT_GENERATOR.get_error_client_alerts(e) == [
            AlertBody(
                alert='Поле «Сумма» содержит неправильное количество символов',
                failed_field='amount',
                failed_field_class_name=None
            )
        ]
    else:
        raise RuntimeError


def test_alert_generator_exact_field_len():
    try:
        Payment(
            src_account=PayerAccountNumber('40802810822200040036'),
            dst_account='40702810438000185552-',
            amount=Amount('1'),
            dst_name=Receiver('Foo'),
            dst_bic=ReceiverBIC('044525225'),
        )
    except Exception as e:
        assert ALERT_GENERATOR.get_error_client_alerts(e) == [
            AlertBody(
                alert='Поле «Счет получателя» должно содержать ровно 20 символов',
                failed_field='receiver account',
                failed_field_class_name='dst_account'
            )
        ]
    else:
        raise RuntimeError


def test_alert_generator_incorrect_data():
    try:
        Payment(
            src_account=PayerAccountNumber('40802810822200040036'),
            dst_account=ReceiverAccountNumber('40702810438000185552'),
            amount=Amount('-1'),
            dst_name=Receiver('Foo'),
            dst_bic=ReceiverBIC('044525225'),
        )
    except Exception as e:
        assert ALERT_GENERATOR.get_error_client_alerts(e) == [
            AlertBody(
                alert='Поле «Сумма» содержит некорректные данные',
                failed_field='amount',
                failed_field_class_name=None
            )
        ]
    else:
        raise RuntimeError


class TestPayerKppChecker(BaseModelChecker):
    payer_kpp: Optional[PayerKPP]
    payment_type: PaymentType
    payer_inn: PayerINN
    payer_status: Optional[PayerStatus]


def test_alert_generator_need_required_field():
    try:
        TestPayerKppChecker(
            payer_kpp=None,
            payment_type=PaymentType.CUSTOMS,
            payer_inn=LE_INN,
            payer_status=None,
        )
    except Exception as e:
        assert ALERT_GENERATOR.get_error_client_alerts(e) == [
            AlertBody(
                alert='Поле «КПП плательщика» должно быть заполнено',
                failed_field='payer kpp',
                failed_field_class_name=None
            )
        ]
    else:
        raise RuntimeError


@pytest.mark.parametrize('wrapped', [False, True])
def test_account_bic_mismatch_alert(wrapped):
    error = ReceiverAccountValidationBICValueError()
    if wrapped:
        error = ValidationError([ErrorWrapper(CheckerError([error]), loc='__root__')], Payment)

    assert ALERT_GENERATOR.get_error_client_alerts(error) == [
        AlertBody(
            alert='Такого счета нет в банке',
            failed_field='receiver account',
            failed_field_class_name=None,
        ),
    ]


@pytest.mark.parametrize('error_type', [
    ReceiverAccountNumberValidationDigitsOnlyError,
    ReceiverAccountValidationFNSValueError,
])
def test_other_receiver_account_errors_keep_generic_alert(error_type):
    assert ALERT_GENERATOR.get_error_client_alerts(error_type()) == [
        AlertBody(
            alert='Поле «Счет получателя» содержит некорректные данные',
            failed_field='receiver account',
            failed_field_class_name=None,
        ),
    ]


def test_missing_receiver_account_keeps_required_alert():
    with pytest.raises(ValidationError) as error:
        Payment(
            src_account='40802810822200040036',
            amount='1',
            dst_name='Foo',
            dst_bic='044525225',
        )

    assert ALERT_GENERATOR.get_error_client_alerts(error.value) == [
        AlertBody(
            alert='Поле «Номер счёта получателя» должно быть заполнено',
            failed_field='receiver_account_number',
            failed_field_class_name='dst_account',
        ),
    ]
