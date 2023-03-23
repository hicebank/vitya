from datetime import date
from typing import ClassVar, Optional

from pydantic import validator

from vitya.payment_order.enums import PaymentType
from vitya.payment_order.fields import (
    UIN,
    AccountNumber,
    Amount,
    Number,
    OperationKind,
    Payee,
    Payer,
    PaymentOrder,
    Purpose,
    PurposeCode,
)
from vitya.payment_order.payments.checkers import (
    AccountBicChecker,
    BaseModelChecker,
    OperationKindChecker,
    PayeeAccountChecker,
    PayerInnChecker,
    PurposeChecker,
    UinChecker,
)
from vitya.payment_order.payments.validators import replace_zero_to_none
from vitya.pydantic_fields import Bic, Inn


class Payment(BaseModelChecker):
    # внутренее поле для типа платежного поручения (зависит от получателя)
    type: PaymentType

    # Наименование расчётного документа (1)
    name: ClassVar[str] = 'Платежное поручение'
    # Форма платёжного поручения (2)
    form: str
    # Номер платёжного поручения (3)
    number: Number
    # Дата составления и оформления (4)
    creation_date: date
    # Вид платежа (5)
    kind: str
    # Сумма (7)
    amount: Amount
    # Сумма прописью (6)
    # TODO: add num2word lib
    amount_str: str = property(fget=lambda self: self.amount)  # type: ignore
    # Плательщик (8)
    payer_name: Payer
    # Счёт плательщика (9)
    payer_account: AccountNumber
    # Наименование банка плательщика (10)
    payer_bank_name: Optional[str]
    # БИК плательщика (11)
    payer_bank_bic: Bic
    # Счёт банка плательщика (12)
    payer_bank_account: AccountNumber
    # Наименование банка получателя (13)
    payee_bank_name: Optional[str]
    # БИК банка получателя (14)
    payee_bank_bic: Bic
    # Счёт банка получателя (15)
    payee_bank_account: Optional[AccountNumber]
    # Наименование получателя (16)
    payee_name: Payee
    # Счёт получателя (17)
    # в каждом типе платежа (_type) проверяется по своему
    payee_account: AccountNumber
    # Вид операции (18)
    operation_kind: OperationKind
    # Срок платежа (19) - количество дней для акцепта
    payment_expire_days: Optional[int]
    # Назначение платежа кодовое (20)
    # в каждом типе платежа (_type) проверяется по своему
    purpose_code: Optional[PurposeCode]
    # Очерёдность платежа (21)
    payment_order: PaymentOrder = PaymentOrder(5)
    # Код (УИН) (22)
    # в каждом типе платежа (_type) проверяется по своему
    uin: Optional[UIN]
    # Резервное поле (23)
    reserve_field: Optional[str]
    # Назначение платежа (24)
    # в каждом типе платежа (_type) проверяется по своему
    purpose: Optional[Purpose]
    # Место для печати (43)

    # Подписи (44)

    # Отметки банка плательщика (45)

    # ИНН плательщика (60)
    # в каждом типе платежа (_type) проверяется по своему
    payer_inn: Optional[Inn]
    # ИНН получателя (61)
    # в каждом типе платежа (_type) проверяется по своему
    payee_inn: Optional[str]
    # Дата поступления в банке плательщика (62)
    bank_income_date: date
    # Дата списания с банка плательщика (71)
    bank_outcome_date: date
    # Статус плательщика (101)
    # в каждом типе платежа (_type) проверяется по своему
    payer_status: Optional[str]
    # КПП плательщика (102)
    # в каждом типе платежа (_type) проверяется по своему
    payer_kpp: Optional[str]
    # КПП получателя (103)
    # в каждом типе платежа (_type) проверяется по своему
    payee_kpp: Optional[str]
    # КБК (104)
    # в каждом типе платежа (_type) проверяется по своему
    cbc: Optional[str]
    # ОКТМО (105)
    # в каждом типе платежа (_type) проверяется по своему
    oktmo: Optional[str]
    # Основание платежа (106)
    # в каждом типе платежа (_type) проверяется по своему
    reason: Optional[str]
    # Периодичность платежа / Код таможенного органа (107)
    # в каждом типе платежа (_type) проверяется по своему
    tax_period: Optional[str]
    # Номер документа (108)
    # в каждом типе платежа (_type) проверяется по своему
    document_number: Optional[str]
    # Номер документа (109)
    # в каждом типе платежа (_type) проверяется по своему
    document_date: Optional[date]

    # Указывает являться ли это платеж за 3-е лицо
    for_third_face: bool = False

    class Config:
        allow_mutation = False

    @validator(
        'purpose_code', 'uin',
        'purpose', 'payer_inn',
        'payee_inn', 'payer_status',
        'payer_kpp', 'payee_kpp',
        'cbc', 'oktmo',
        'reason', 'tax_period',
        'document_number', 'document_date',
        pre=True
    )
    def transform_zeros(cls, value: Optional[str]) -> Optional[str]:
        return replace_zero_to_none(value=value)

    __checkers__ = [
        (OperationKindChecker, ['operation_kind', 'type']),
        (AccountBicChecker, ['payer_account', 'payer_bic']),
        (PayeeAccountChecker, ['payee_account', 'payee_bic', 'type']),
        (PayerInnChecker, ['payer_inn', 'payer_status', 'for_third_face', 'type']),
        (UinChecker, ['uin', 'payer_inn', 'payer_status', 'type']),
        (PurposeChecker, ['purpose', 'type']),
    ]
