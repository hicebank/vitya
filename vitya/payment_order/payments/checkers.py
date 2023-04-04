from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, List, Tuple, Type, cast

from pydantic import BaseModel, root_validator
from pydantic.errors import PydanticValueError

from vitya.payment_order.enums import PaymentType
from vitya.payment_order.fields import (
    AccountNumber,
    OperationKind,
    PayerStatus,
    Purpose,
    Uin,
)
from vitya.payment_order.payments.validators import (
    validate_account_by_bic,
    validate_operation_kind,
    validate_payee_account,
    validate_payee_inn,
    validate_payee_kpp,
    validate_payer_inn,
    validate_payer_kpp,
    validate_payer_status,
    validate_purpose,
    validate_uin,
)
from vitya.pydantic_fields import Bic, Inn, Kpp


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

    @root_validator(pre=False)
    def run_checkers(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        errors = []
        for checker, fields_names in cls.__checkers__:
            try:
                args = [values[field_name] for field_name in fields_names]
            except KeyError:
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
    def __init__(self, account_number: AccountNumber, bic: Bic) -> None:
        self.account_number = account_number
        self.bic = bic

    def check(self) -> None:
        validate_account_by_bic(account_number=self.account_number, bic=self.bic)


class PayeeAccountChecker(BaseChecker):
    def __init__(self, account_number: AccountNumber, bic: Bic, payment_type: PaymentType) -> None:
        self.account_number = account_number
        self.bic = bic
        self.payment_type = payment_type

    def check(self) -> None:
        validate_payee_account(value=self.account_number, payee_bic=self.bic, payment_type=self.payment_type)


class OperationKindChecker(BaseChecker):
    def __init__(self, operation_kind: OperationKind, payment_type: PaymentType) -> None:
        self.operation_kind = operation_kind
        self.payment_type = payment_type

    def check(self) -> None:
        validate_operation_kind(value=self.operation_kind, payment_type=self.payment_type)


class PayerInnChecker(BaseChecker):
    def __init__(
        self,
        payer_inn: Inn,
        payer_status: PayerStatus,
        for_third_face: bool,
        payment_type: PaymentType
    ) -> None:
        self.payer_inn = payer_inn
        self.payer_status = payer_status
        self.for_third_face = for_third_face
        self.payment_type = payment_type

    def check(self) -> None:
        validate_payer_inn(
            value=self.payer_inn,
            payment_type=self.payment_type,
            payer_status=self.payer_status,
            for_third_face=self.for_third_face,
        )


class UinChecker(BaseChecker):
    def __init__(self, uin: Uin, payer_inn: Inn, payer_status: PayerStatus, payment_type: PaymentType) -> None:
        self.uin = uin
        self.payer_inn = payer_inn
        self.payer_status = payer_status
        self.payment_type = payment_type

    def check(self) -> None:
        validate_uin(
            value=self.uin,
            payment_type=self.payment_type,
            payer_inn=self.payer_inn,
            payer_status=self.payer_status,
        )


class PurposeChecker(BaseChecker):
    def __init__(self, purpose: Purpose, payment_type: PaymentType) -> None:
        self.purpose = purpose
        self.payment_type = payment_type

    def check(self) -> None:
        validate_purpose(value=self.purpose, payment_type=self.payment_type)


class PayeeInnChecker(BaseChecker):
    def __init__(
        self,
        payee_inn: Inn,
        payment_type: PaymentType
    ) -> None:
        self.payee_inn = payee_inn
        self.payment_type = payment_type

    def check(self) -> None:
        validate_payee_inn(value=self.payee_inn, payment_type=self.payment_type)


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
        validate_payer_status(
            value=self.payer_status,
            payment_type=self.payment_type,
            for_third_face=self.for_third_face
        )


class PayerKppChecker(BaseChecker):
    def __init__(
        self,
        payer_kpp: Kpp,
        payment_type: PaymentType,
        payer_inn: Inn,
    ) -> None:
        self.payer_kpp = payer_kpp
        self.payment_type = payment_type
        self.payer_inn = payer_inn

    def check(self) -> None:
        validate_payer_kpp(
            value=self.payer_kpp,
            payment_type=self.payment_type,
            payer_inn=self.payer_inn
        )


class PayeeKppChecker(BaseChecker):
    def __init__(
        self,
        payee_kpp: Kpp,
        payment_type: PaymentType,
    ) -> None:
        self.payee_kpp = payee_kpp
        self.payment_type = payment_type

    def check(self) -> None:
        validate_payee_kpp(
            value=self.payee_kpp,
            payment_type=self.payment_type,
        )
