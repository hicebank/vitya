from typing import Optional

from tests.payment_order.testdata import LE_INN
from vitya.error_description import AlertBody, AlertGenerator
from vitya.payment_order.enums import PaymentType
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
from vitya.payment_order.payments.checkers import BaseModelChecker


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
