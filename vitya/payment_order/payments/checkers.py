from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, List, Tuple, Type, cast

from pydantic import BaseModel, root_validator
from pydantic.errors import PydanticValueError

from vitya.payment_order.enums import PaymentType
from vitya.payment_order.fields import (
    CBC,
    UIN,
    AccountNumber,
    DocumentDate,
    DocumentNumber,
    OperationKind,
    PayerStatus,
    Purpose,
    Reason,
    TaxPeriod,
)
from vitya.payment_order.payments.checks import (
    check_account_by_bic,
    check_cbc,
    check_document_date,
    check_document_number,
    check_oktmo,
    check_operation_kind,
    check_payee_account,
    check_payee_inn,
    check_payee_kpp,
    check_payer_inn,
    check_payer_kpp,
    check_payer_status,
    check_purpose,
    check_reason,
    check_tax_period,
    check_uin,
)
from vitya.pydantic_fields import BIC, INN, KPP, OKTMO


class CheckerError(ValueError):
    @property
    def errors(self) -> List[Type[PydanticValueError]]:
        return cast(List[Type[PydanticValueError]], self.args[0])


class BaseChecker(ABC):
    @abstractmethod
    def check(self) -> None:  # pragma: no cover
        pass


class BaseModelChecker(BaseModel):
    __checkers__: ClassVar[List[Tuple[Type[BaseChecker], List[str]]]] = []

    def __init_subclass__(cls, **kwargs: Dict[str, Any]) -> None:  # pragma: no cover
        # built error
        errors = []
        for checker, fields in cls.__checkers__:
            wild_fields = set(fields) - cls.__fields__.keys()
            if wild_fields:
                errors.append(ValueError(f'Checker {checker} require unknown model fields {wild_fields}'))
        if errors:
            raise CheckerError(errors)

    @root_validator(pre=False)
    def run_checkers(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        errors = []
        for checker, fields_names in cls.__checkers__:
            try:
                args = [values[field_name] for field_name in fields_names]
            except KeyError:  # pragma: no cover
                continue
            else:
                try:
                    checker(*args).check()
                except Exception as e:
                    errors.append(e)
        if errors:
            raise CheckerError(errors)
        return values


class AccountBicChecker(BaseChecker):
    def __init__(self, account_number: AccountNumber, bic: BIC) -> None:
        self.account_number = account_number
        self.bic = bic

    def check(self) -> None:
        check_account_by_bic(account_number=self.account_number, bic=self.bic)


class PayeeAccountChecker(BaseChecker):
    def __init__(self, account_number: AccountNumber, bic: BIC, payment_type: PaymentType) -> None:
        self.account_number = account_number
        self.bic = bic
        self.payment_type = payment_type

    def check(self) -> None:
        check_payee_account(value=self.account_number, payment_type=self.payment_type, payee_bic=self.bic)


class OperationKindChecker(BaseChecker):
    def __init__(self, operation_kind: OperationKind, payment_type: PaymentType) -> None:
        self.operation_kind = operation_kind
        self.payment_type = payment_type

    def check(self) -> None:
        check_operation_kind(value=self.operation_kind, payment_type=self.payment_type)


class PayerINNChecker(BaseChecker):
    def __init__(
        self,
        payer_inn: INN,
        payer_status: PayerStatus,
        for_third_face: bool,
        payment_type: PaymentType
    ) -> None:
        self.payer_inn = payer_inn
        self.payer_status = payer_status
        self.for_third_face = for_third_face
        self.payment_type = payment_type

    def check(self) -> None:
        check_payer_inn(
            value=self.payer_inn,
            payment_type=self.payment_type,
            payer_status=self.payer_status,
            for_third_face=self.for_third_face
        )


class UINChecker(BaseChecker):
    def __init__(self, uin: UIN, payer_inn: INN, payer_status: PayerStatus, payment_type: PaymentType) -> None:
        self.uin = uin
        self.payer_inn = payer_inn
        self.payer_status = payer_status
        self.payment_type = payment_type

    def check(self) -> None:
        check_uin(
            value=self.uin,
            payment_type=self.payment_type,
            payer_status=self.payer_status,
            payer_inn=self.payer_inn,
        )


class PurposeChecker(BaseChecker):
    def __init__(self, purpose: Purpose, payment_type: PaymentType) -> None:
        self.purpose = purpose
        self.payment_type = payment_type

    def check(self) -> None:
        check_purpose(value=self.purpose, payment_type=self.payment_type)


class PayeeINNChecker(BaseChecker):
    def __init__(
        self,
        payee_inn: INN,
        payment_type: PaymentType
    ) -> None:
        self.payee_inn = payee_inn
        self.payment_type = payment_type

    def check(self) -> None:
        check_payee_inn(value=self.payee_inn, payment_type=self.payment_type)


class PayerStatusChecker(BaseChecker):
    def __init__(
        self,
        payer_status: PayerStatus,
        payment_type: PaymentType,
        for_third_face: bool,
    ) -> None:
        self.payer_status = payer_status
        self.payment_type = payment_type
        self.for_third_face = for_third_face

    def check(self) -> None:
        check_payer_status(value=self.payer_status, payment_type=self.payment_type, for_third_face=self.for_third_face)


class PayerKPPChecker(BaseChecker):
    def __init__(
        self,
        payer_kpp: KPP,
        payment_type: PaymentType,
        payer_inn: INN,
    ) -> None:
        self.payer_kpp = payer_kpp
        self.payment_type = payment_type
        self.payer_inn = payer_inn

    def check(self) -> None:
        check_payer_kpp(value=self.payer_kpp, payment_type=self.payment_type, payer_inn=self.payer_inn)


class PayeeKPPChecker(BaseChecker):
    def __init__(
        self,
        payee_kpp: KPP,
        payment_type: PaymentType,
    ) -> None:
        self.payee_kpp = payee_kpp
        self.payment_type = payment_type

    def check(self) -> None:
        check_payee_kpp(value=self.payee_kpp, payment_type=self.payment_type)


class CBCChecker(BaseChecker):
    def __init__(
        self,
        cbc: CBC,
        payment_type: PaymentType,
    ) -> None:
        self.cbc = cbc
        self.payment_type = payment_type

    def check(self) -> None:
        check_cbc(value=self.cbc, payment_type=self.payment_type)


class OKTMOChecker(BaseChecker):
    def __init__(
        self,
        oktmo: OKTMO,
        payment_type: PaymentType,
        payer_status: PayerStatus,
    ) -> None:
        self.oktmo = oktmo
        self.payment_type = payment_type
        self.payer_status = payer_status

    def check(self) -> None:
        check_oktmo(value=self.oktmo, payment_type=self.payment_type, payer_status=self.payer_status)


class ReasonChecker(BaseChecker):
    def __init__(
        self,
        reason: Reason,
        payment_type: PaymentType,
    ) -> None:
        self.reason = reason
        self.payment_type = payment_type

    def check(self) -> None:
        check_reason(value=self.reason, payment_type=self.payment_type)


class TaxPeriodChecker(BaseChecker):
    def __init__(
        self,
        tax_period: TaxPeriod,
        payment_type: PaymentType,
        payer_status: PayerStatus,
    ) -> None:
        self.tax_period = tax_period
        self.payment_type = payment_type
        self.payer_status = payer_status

    def check(self) -> None:
        check_tax_period(value=self.tax_period, payment_type=self.payment_type, payer_status=self.payer_status)


class DocumentNumberChecker(BaseChecker):
    def __init__(
        self,
        document_number: DocumentNumber,
        payment_type: PaymentType,
        reason: Reason,
        payer_status: PayerStatus,
        payee_account: AccountNumber,
        uin: UIN,
        payer_inn: INN,
    ) -> None:
        self.document_number = document_number
        self.payment_type = payment_type
        self.reason = reason
        self.payer_status = payer_status
        self.payee_account = payee_account
        self.uin = uin
        self.payer_inn = payer_inn

    def check(self) -> None:
        check_document_number(
            value=self.document_number,
            payment_type=self.payment_type,
            reason=self.reason,
            payer_status=self.payer_status,
            payee_account=self.payee_account,
            uin=self.uin,
            payer_inn=self.payer_inn,
        )


class DocumentDateChecker(BaseChecker):
    def __init__(
        self,
        document_date: DocumentDate,
        payment_type: PaymentType,
    ) -> None:
        self.document_date = document_date
        self.payment_type = payment_type

    def check(self) -> None:
        check_document_date(value=self.document_date, payment_type=self.payment_type)
