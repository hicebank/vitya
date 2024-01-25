from typing import Optional, Union

from vitya.payment_order.enums import PaymentType
from vitya.payment_order.fields import (
    CBC,
    UIN,
    Amount,
    DocumentDate,
    DocumentNumber,
    ForThirdPerson,
    Number,
    OperationKind,
    PayerAccountNumber,
    PayerINN,
    PayerKPP,
    PayerStatus,
    PaymentOrder,
    Purpose,
    Reason,
    Receiver,
    ReceiverAccountNumber,
    ReceiverBIC,
    ReceiverINN,
    ReceiverKPP,
    TaxPeriod,
)
from vitya.payment_order.payments.checkers import (
    BaseChecker,
    BaseModelChecker,
    CBCChecker,
    DocumentDateChecker,
    DocumentDateWithReasonChecker,
    DocumentNumberChecker,
    OKTMOChecker,
    OKTMOWithPayerStatusChecker,
    OKTMOWithReceiverAccountNumberChecker,
    OperationKindChecker,
    PayerINNChecker,
    PayerKPPChecker,
    PayerStatusChecker,
    PaymentTypeAndForThirdPersonChecker,
    ForThirdPersonAndPurposeChecker,
    PurposeChecker,
    ReasonChecker,
    ReceiverAccountChecker,
    ReceiverAccountCheckerWithPaymentType,
    ReceiverINNChecker,
    ReceiverKPPChecker,
    TaxPeriodChecker,
    UINChecker,
)
from vitya.pydantic_fields import OKTMO


def test_auto_wiring_non_unions():
    class Payment(BaseModelChecker):
        account_number: ReceiverAccountNumber
        bic: ReceiverBIC
        payment_type: PaymentType

    assert Payment.__final_wired_checkers__ == [
        (ReceiverAccountChecker, ['account_number', 'bic', 'payment_type']),
        (ReceiverAccountCheckerWithPaymentType, ['account_number', 'payment_type']),
    ]

    class PaymentWithOperationKind(Payment):
        operation_kind: OperationKind

    assert PaymentWithOperationKind.__final_wired_checkers__ == [
        (ReceiverAccountChecker, ['account_number', 'bic', 'payment_type']),
        (ReceiverAccountCheckerWithPaymentType, ['account_number', 'payment_type']),
        (OperationKindChecker, ['operation_kind', 'payment_type']),
    ]


def test_auto_wiring_same_unions():
    class Payment(BaseModelChecker):
        purpose: Optional[Purpose]
        payment_type: PaymentType
        payer_account: PayerAccountNumber

    assert Payment.__final_wired_checkers__ == [
        (PurposeChecker, ['purpose', 'payment_type', 'payer_account']),
    ]


def test_auto_wiring_union_subset():
    class Payment(BaseModelChecker):
        purpose: Purpose
        payment_type: PaymentType
        payer_account: PayerAccountNumber

    assert Payment.__final_wired_checkers__ == [
        (PurposeChecker, ['purpose', 'payment_type', 'payer_account']),
    ]


def test_auto_wiring_union_superset():
    class Payment(BaseModelChecker):
        purpose: Union[Purpose, None, bool]
        payment_type: PaymentType
        payer_account: PayerAccountNumber

    assert Payment.__final_wired_checkers__ == []


def test_auto_wiring_complex():
    class BasePayment(BaseModelChecker):
        src_inn: Optional[PayerINN]  # [60]
        src_kpp: Optional[PayerKPP]  # [102]

        doc_num: Optional[Number]  # [3]

        src_account: PayerAccountNumber  # [9]
        dst_account: ReceiverAccountNumber  # [17]
        amount: Optional[Amount]  # [7]
        currency: str  # [21]
        priority: Optional[PaymentOrder]  # [21]
        payment_channel: Optional[str]
        dst_name: Receiver  # [16]
        dst_inn: Optional[ReceiverINN]  # [61]
        dst_bic: ReceiverBIC  # [14]
        purpose: Optional[Purpose]  # [24]
        dst_kpp: Optional[ReceiverKPP]  # [103]
        reason: Optional[Reason]  # [106]
        ts: Optional[PayerStatus]  # [101] tax payer status
        tp: Optional[TaxPeriod]  # [107] tax period
        tn: Optional[DocumentNumber]  # [108] tax payment number
        td: Optional[DocumentDate]  # [109] tax payment date
        cbccode: Optional[CBC]  # [104]
        oktmo: Optional[OKTMO]  # [105]
        uin: Optional[UIN] = None  # [22]

    assert BasePayment.__final_wired_checkers__ == []

    class Payment(BasePayment):
        for_third_person: ForThirdPerson
        payment_type: PaymentType

    assert Payment.__final_wired_checkers__ == [
        (ReceiverAccountChecker, ['dst_account', 'dst_bic', 'payment_type']),
        (ReceiverAccountCheckerWithPaymentType, ['dst_account', 'payment_type']),
        (PayerINNChecker, ['src_inn', 'ts', 'for_third_person', 'payment_type']),
        (UINChecker, ['uin', 'dst_account', 'src_inn', 'ts', 'payment_type']),
        (PurposeChecker, ['purpose', 'payment_type', 'src_account']),
        (ReceiverINNChecker, ['dst_inn', 'payment_type']),
        (PayerStatusChecker, ['ts', 'payment_type', 'for_third_person']),
        (PaymentTypeAndForThirdPersonChecker, ['payment_type', 'for_third_person']),
        (ForThirdPersonAndPurposeChecker, ['purpose', 'for_third_person']),
        (PayerKPPChecker, ['src_kpp', 'payment_type', 'src_inn']),
        (ReceiverKPPChecker, ['dst_kpp', 'payment_type']),
        (CBCChecker, ['cbccode', 'payment_type']),
        (OKTMOChecker, ['oktmo', 'payment_type']),
        (OKTMOWithPayerStatusChecker, ['oktmo', 'payment_type', 'ts']),
        (OKTMOWithReceiverAccountNumberChecker, ['oktmo', 'payment_type', 'dst_account']),
        (ReasonChecker, ['reason', 'payment_type']),
        (TaxPeriodChecker, ['tp', 'payment_type', 'ts']),
        (DocumentNumberChecker, ['tn', 'payment_type', 'reason', 'ts', 'dst_account', 'uin', 'src_inn']),
        (DocumentDateChecker, ['td', 'payment_type']),
        (DocumentDateWithReasonChecker, ['td', 'payment_type', 'reason']),
    ]


def test_auto_wiring_all_checkers():
    class Payment(BaseModelChecker):
        src_inn: Optional[PayerINN]  # [60]
        src_kpp: Optional[PayerKPP]  # [102]

        doc_num: Optional[Number]  # [3]

        src_account: PayerAccountNumber  # [9]
        dst_account: ReceiverAccountNumber  # [17]
        amount: Optional[Amount]  # [7]
        currency: str  # [21]
        priority: Optional[PaymentOrder]  # [21]
        payment_channel: Optional[str]
        dst_name: Receiver  # [16]
        dst_inn: Optional[ReceiverINN]  # [61]
        dst_bic: ReceiverBIC  # [14]
        purpose: Optional[Purpose]  # [24]
        dst_kpp: Optional[ReceiverKPP]  # [103]
        reason: Optional[Reason]  # [106]
        ts: Optional[PayerStatus]  # [101] tax payer status
        tp: Optional[TaxPeriod]  # [107] tax period
        tn: Optional[DocumentNumber]  # [108] tax payment number
        td: Optional[DocumentDate]  # [109] tax payment date
        cbccode: Optional[CBC]  # [104]
        oktmo: Optional[OKTMO]  # [105]
        uin: Optional[UIN] = None  # [22]

        op_kind: OperationKind

        for_third_person: ForThirdPerson
        payment_type: PaymentType

    assert Payment.__final_wired_checkers__ == [
        (ReceiverAccountChecker, ['dst_account', 'dst_bic', 'payment_type']),
        (ReceiverAccountCheckerWithPaymentType, ['dst_account', 'payment_type']),
        (OperationKindChecker, ['op_kind', 'payment_type']),
        (PayerINNChecker, ['src_inn', 'ts', 'for_third_person', 'payment_type']),
        (UINChecker, ['uin', 'dst_account', 'src_inn', 'ts', 'payment_type']),
        (PurposeChecker, ['purpose', 'payment_type', 'src_account']),
        (ReceiverINNChecker, ['dst_inn', 'payment_type']),
        (PayerStatusChecker, ['ts', 'payment_type', 'for_third_person']),
        (PaymentTypeAndForThirdPersonChecker, ['payment_type', 'for_third_person']),
        (ForThirdPersonAndPurposeChecker, ['purpose', 'for_third_person']),
        (PayerKPPChecker, ['src_kpp', 'payment_type', 'src_inn']),
        (ReceiverKPPChecker, ['dst_kpp', 'payment_type']),
        (CBCChecker, ['cbccode', 'payment_type']),
        (OKTMOChecker, ['oktmo', 'payment_type']),
        (OKTMOWithPayerStatusChecker, ['oktmo', 'payment_type', 'ts']),
        (OKTMOWithReceiverAccountNumberChecker, ['oktmo', 'payment_type', 'dst_account']),
        (ReasonChecker, ['reason', 'payment_type']),
        (TaxPeriodChecker, ['tp', 'payment_type', 'ts']),
        (DocumentNumberChecker, ['tn', 'payment_type', 'reason', 'ts', 'dst_account', 'uin', 'src_inn']),
        (DocumentDateChecker, ['td', 'payment_type']),
        (DocumentDateWithReasonChecker, ['td', 'payment_type', 'reason']),
    ]
    assert len(Payment.__final_wired_checkers__) == len(Payment.__auto_checkers__)


def test_auto_wiring_excluding():
    class Payment(BaseModelChecker):
        account_number: ReceiverAccountNumber
        bic: ReceiverBIC
        payment_type: PaymentType
        operation_kind: OperationKind

        __excluded_auto_checkers__ = {}

    assert Payment.__final_wired_checkers__ == [
        (ReceiverAccountChecker, ['account_number', 'bic', 'payment_type']),
        (ReceiverAccountCheckerWithPaymentType, ['account_number', 'payment_type']),
        (OperationKindChecker, ['operation_kind', 'payment_type']),
    ]

    class PaymentExcludeOne(Payment):
        __excluded_auto_checkers__ = {OperationKindChecker}

    assert PaymentExcludeOne.__final_wired_checkers__ == [
        (ReceiverAccountChecker, ['account_number', 'bic', 'payment_type']),
        (ReceiverAccountCheckerWithPaymentType, ['account_number', 'payment_type']),
    ]

    class PaymentExcludeTwo(Payment):
        __excluded_auto_checkers__ = {OperationKindChecker, ReceiverAccountChecker, ReceiverAccountCheckerWithPaymentType}

    assert PaymentExcludeTwo.__final_wired_checkers__ == []


def test_auto_wiring_disabling():
    class Payment(BaseModelChecker):
        account_number: ReceiverAccountNumber
        bic: ReceiverBIC
        payment_type: PaymentType
        operation_kind: OperationKind

        __wire_auto_checkers__ = False

    assert Payment.__final_wired_checkers__ == []


def test_extra_wired_checkers():
    class MyChecker(BaseChecker):
        def __init__(self, bic: ReceiverBIC, operation_kind: OperationKind):
            pass

        def check(self) -> None:
            pass

    class Payment(BaseModelChecker):
        account_number: ReceiverAccountNumber
        bic: ReceiverBIC
        payment_type: PaymentType
        operation_kind: OperationKind

        __extra_wired_checkers__ = [
            (MyChecker, ['bic', 'operation_kind'])
        ]

    assert Payment.__final_wired_checkers__ == [
        (MyChecker, ['bic', 'operation_kind']),
        (ReceiverAccountChecker, ['account_number', 'bic', 'payment_type']),
        (ReceiverAccountCheckerWithPaymentType, ['account_number', 'payment_type']),
        (OperationKindChecker, ['operation_kind', 'payment_type']),
    ]


def test_extra_wired_checkers_and_auto_wiring_disabling():
    class MyChecker(BaseChecker):
        def __init__(self, bic: ReceiverBIC, operation_kind: OperationKind):
            pass

        def check(self) -> None:
            pass

    class Payment(BaseModelChecker):
        account_number: ReceiverAccountNumber
        bic: ReceiverBIC
        payment_type: PaymentType
        operation_kind: OperationKind

        __wire_auto_checkers__ = False
        __extra_wired_checkers__ = [
            (MyChecker, ['bic', 'operation_kind'])
        ]

    assert Payment.__final_wired_checkers__ == [
        (MyChecker, ['bic', 'operation_kind']),
    ]
