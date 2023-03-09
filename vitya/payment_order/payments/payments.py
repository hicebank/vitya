from decimal import Decimal
from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, Field, validator

from vitya.payment_order.enums import PaymentType
from vitya.payment_order.fields import Payee, Payer, PaymentOrder
from vitya.payment_order.payments.validators import validate_payment_data
from vitya.pydantic_fields import Bic


class Payment(BaseModel):
    # внутренее поле для типа платежного поручения (зависит от получателя)
    _type: PaymentType

    # Наименование расчётного документа (1)
    name: str = 'Платежное поручение'
    # Форма платёжного поручения (2)
    form: str = Field(max_length=6)
    # Номер платёжного поручения (3)
    number: str
    # Дата составления и оформления (4)
    date: date
    # Вид платежа (5)
    kind: str
    # Сумма (7)
    amount: Decimal
    # Сумма прописью (6)
    amount_str: str = property(fget=lambda self: self.amount)
    # Плательщик (8)
    payer_name: Payer
    # Счёт плательщика (9)
    payer_account: str
    # Наименование банка плательщика (10)
    payer_bank_name: Optional[str]
    # БИК плательщика (11)
    payer_bank_bic: Bic
    # Счёт банка плательщика (12)
    payer_bank_account: Optional[str]
    # Наименование банка получателя (13)
    payee_bank_name: Optional[str]
    # БИК банка получателя (14)
    payee_bank_bic: Bic
    # Счёт банка получателя (15)
    payee_bank_account: Optional[str]
    # Наименование получателя (16)
    payee_name: Payee
    # Счёт получателя (17)
    # в каждом типе платежа (_type) проверяется по своему
    payee_account: str
    # Вид операции (18)
    operation_kind: str
    # Срок платежа (19) - количество дней для акцепта
    payment_expire_days: Optional[int]
    # Назначение платежа кодовое (20)
    # в каждом типе платежа (_type) проверяется по своему
    purpose_code: Optional[int]
    # Очерёдность платежа (21)
    payment_order: PaymentOrder = 5
    # Код (УИН) (22)
    # в каждом типе платежа (_type) проверяется по своему
    uin: str
    # Резервное поле (23)
    reserve_field: Optional[str]
    # Назначение платежа
    # в каждом типе платежа (_type) проверяется по своему
    purpose: Optional[str]
    # Место для печати (43)

    # Подписи (44)

    # Отметки банка плательщика (45)

    # ИНН плательщика (60)
    # в каждом типе платежа (_type) проверяется по своему
    payer_inn: str
    # ИНН получателя (61)
    # в каждом типе платежа (_type) проверяется по своему
    payee_inn: str
    # Дата поступления в банке плательщика (62)
    bank_income_date: date
    # Дата списания с банка плательщика (71)
    bank_outcome_date: date
    # Статус плательщика (101)
    # в каждом типе платежа (_type) проверяется по своему
    payer_status: str
    # КПП плательщика (102)
    # в каждом типе платежа (_type) проверяется по своему
    payer_kpp: str
    # КПП получателя (103)
    # в каждом типе платежа (_type) проверяется по своему
    payee_kpp: str
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

    @validator('*', pre=True)
    def validate(cls, values: dict[str, Any]) -> dict[str, Any]:
        return validate_payment_data(
            _type=values['_type'],
            name=values['name'],
            form=values['form'],
            number=values['number'],
            date=values['date'],
            kind=values['kind'],
            amount=values['amount'],
            amount_str=values['amount_str'],
            payer_name=values['payer_name'],
            payer_account=values['payer_account'],
            payer_bank_name=values['payer_bank_name'],
            payer_bank_bic=values['payer_bank_bic'],
            payer_bank_account=values['payer_bank_account'],
            payee_bank_name=values['payee_bank_name'],
            payee_bank_bic=values['payee_bank_bic'],
            payee_bank_account=values['payee_bank_account'],
            payee_name=values['payee_name'],
            payee_account=values['payee_account'],
            operation_kind=values['operation_kind'],
            payment_expire_days=values['payment_expire_days'],
            purpose_code=values['purpose_code'],
            payment_order=values['payment_order'],
            uin=values['uin'],
            reserve_field=values['reserve_field'],
            purpose=values['purpose'],
            payer_inn=values['payer_inn'],
            payee_inn=values['payee_inn'],
            bank_income_date=values['bank_income_date'],
            bank_outcome_date=values['bank_outcome_date'],
            payer_status=values['payer_status'],
            payer_kpp=values['payer_kpp'],
            payee_kpp=values['payee_kpp'],
            cbc=values['cbc'],
            oktmo=values['oktmo'],
            reason=values['reason'],
            tax_period=values['tax_period'],
            document_number=values['document_number'],
            document_date=values['document_date'],
        )
