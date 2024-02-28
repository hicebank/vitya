from decimal import Decimal
from typing import Any, Callable, Generator, Optional

from vitya.payment_order.validators import (
    validate_account_number,
    validate_amount,
    validate_cbc,
    validate_customer,
    validate_document_date,
    validate_document_number,
    validate_number,
    validate_operation_kind,
    validate_payer,
    validate_payer_kpp,
    validate_payer_status,
    validate_payment_order,
    validate_purpose,
    validate_purpose_code,
    validate_reason,
    validate_receiver,
    validate_receiver_account_number,
    validate_receiver_kpp,
    validate_tax_period,
    validate_type_of_income,
    validate_uin,
)
from vitya.pydantic_fields import BIC, INN, KPP, BoolWrapper, FieldMixin

CallableGenerator = Generator[Callable[..., Any], None, None]


class Number(FieldMixin, str):
    """Номер платёжного поручения (3)"""

    @classmethod
    def _validate(cls, value: str) -> str:
        return validate_number(value)


class Amount(FieldMixin, Decimal):
    """Сумма (7)"""

    @classmethod
    def _validate(cls, value: str) -> Decimal:
        return validate_amount(value)


class Customer(FieldMixin, str):
    """Общий класс для описания сущности владельца денег"""

    @classmethod
    def _validate(cls, value: str) -> str:
        return validate_customer(value)


class Payer(Customer):
    """Плательщик (8)"""

    @classmethod
    def _validate(cls, value: str) -> str:
        return validate_payer(value)


class Receiver(Customer):
    """Наименование получателя (16)"""

    @classmethod
    def _validate(cls, value: str) -> str:
        return validate_receiver(value)


class PaymentOrder(FieldMixin, int):
    """Очерёдность платежа (21)"""

    @classmethod
    def _validate(cls, value: str) -> int:
        return validate_payment_order(value)


class AccountNumber(FieldMixin, str):
    """Счёт"""

    @classmethod
    def _validate(cls, value: str) -> str:
        return validate_account_number(value)


class ReceiverAccountNumber(AccountNumber):
    """Счет получателя (17)"""

    @classmethod
    def _validate(cls, value: str) -> str:
        return validate_receiver_account_number(value)


class PayerAccountNumber(AccountNumber):
    """Номер счёта плательщика (9)"""


class OperationKind(FieldMixin, str):
    """Вид операции (18)"""

    @classmethod
    def _validate(cls, value: str) -> str:
        return validate_operation_kind(value)


class UIN(FieldMixin, str):
    """Код (УИН) (22)"""

    @classmethod
    def _validate(cls, value: str) -> Optional[str]:
        return validate_uin(value)


class PurposeCode(FieldMixin, int):
    """Назначение платежа кодовое (20)"""

    @classmethod
    def _validate(cls, value: int) -> int:
        return validate_purpose_code(value)


class Purpose(FieldMixin, str):
    """Назначение платежа (24)"""

    @classmethod
    def _validate(cls, value: str) -> Optional[str]:
        return validate_purpose(value)


class PayerINN(INN):
    """ИНН плательщика (60)"""


class ReceiverINN(INN):
    """ИНН получателя (61)"""


class ReceiverBIC(BIC):
    """БИК банка получателя (14)"""


class ReceiverKPP(KPP):
    """КПП плательщика (103)"""

    @classmethod
    def _validate(cls, value: str) -> Optional[str]:
        return validate_receiver_kpp(value)


class PayerKPP(KPP):
    """КПП получателя (102)"""

    @classmethod
    def _validate(cls, value: str) -> Optional[str]:
        return validate_payer_kpp(value)


class PayerStatus(FieldMixin, str):
    """Статус плательщика (101)"""

    @classmethod
    def _validate(cls, value: str) -> str:
        return validate_payer_status(value)


class CBC(FieldMixin, str):
    """КБК (104)"""

    @classmethod
    def _validate(cls, value: str) -> Optional[str]:
        return validate_cbc(value)


class Reason(FieldMixin, str):
    """Основание платежа (106)"""

    @classmethod
    def _validate(cls, value: str) -> Optional[str]:
        return validate_reason(value)


class TaxPeriod(FieldMixin, str):
    """Периодичность платежа / Код таможенного органа (107)"""

    @classmethod
    def _validate(cls, value: str) -> Optional[str]:
        return validate_tax_period(value)


class DocumentNumber(FieldMixin, str):
    """Номер документа (108)"""

    @classmethod
    def _validate(cls, value: str) -> Optional[str]:
        return validate_document_number(value)


class DocumentDate(FieldMixin, str):
    """Дата документа (109)"""

    @classmethod
    def _validate(cls, value: str) -> Optional[str]:
        return validate_document_date(value)


class ForThirdPerson(BoolWrapper):
    pass


class TypeOfIncome(FieldMixin, str):
    """Код вида дохода"""

    @classmethod
    def _validate(cls, value: str) -> Optional[str]:
        return validate_type_of_income(value)
