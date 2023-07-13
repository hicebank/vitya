from typing import Optional

from vitya.error_description import AlertGenerator
from vitya.payment_order.fields import (
    Amount,
    PayerAccountNumber,
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


def test_alert_generator_amount():
    alert_generator = AlertGenerator(
        {
            'amount': 'amount',
            'payer': 'dst_name',
            'receiver_bic': 'dst_bic',
            'receiver': 'dst_name',
            'receiver_account_number': 'dst_account',
        }
    )
    try:
        Payment(
            src_account=PayerAccountNumber('40802810822200040036'),
            dst_account=ReceiverAccountNumber('40702810438000185552'),
            amount=None,
            dst_name=Receiver('Foo'),
            dst_bic=ReceiverBIC('044525225'),
        )
    except Exception as e:
        assert alert_generator.get_error_client_alerts(e) == ['Поле «Сумма» должно быть заполнено']
    else:
        raise RuntimeError
