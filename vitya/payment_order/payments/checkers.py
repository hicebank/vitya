from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, List, Tuple, Type

from pydantic import BaseModel, root_validator

from vitya.payment_order.enums import PaymentType
from vitya.payment_order.fields import UIN, AccountNumber, OperationKind, PayerStatus
from vitya.payment_order.payments.validators import (
    validate_account_by_bic,
    validate_operation_kind,
    validate_payee_account,
    validate_payer_inn,
    validate_purpose,
    validate_uin,
)
from vitya.pydantic_fields import Bic, Inn


class BaseChecker(ABC):
    @abstractmethod
    def check(self) -> None:
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
            raise ValueError(errors)
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
    def __init__(self, uin: UIN, payer_inn: Inn, payer_status: PayerStatus, payment_type: PaymentType) -> None:
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
    def __init__(self, purpose: str, payment_type: PaymentType) -> None:
        self.purpose = purpose
        self.payment_type = payment_type

    def check(self) -> None:
        validate_purpose(value=self.purpose, payment_type=self.payment_type)
