from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, List, Tuple, Type

from pydantic import BaseModel, root_validator

from vitya.payment_order.enums import PaymentType
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
    def __init__(self, account_number: str, bic: Bic) -> None:
        self.account_number = account_number
        self.bic = bic

    def check(self) -> None:
        validate_account_by_bic(account_number=self.account_number, bic=self.bic)


class PayeeAccountChecker(BaseChecker):
    def __init__(self, account_number: str, bic: Bic, _type: PaymentType) -> None:
        self.account_number = account_number
        self.bic = bic
        self.type = _type

    def check(self) -> None:
        validate_payee_account(value=self.account_number, payee_bic=self.bic, _type=self.type)


class OperationKindChecker(BaseChecker):
    def __init__(self, operation_kind: str, _type: PaymentType) -> None:
        self.operation_kind = operation_kind
        self.type = _type

    def check(self) -> None:
        validate_operation_kind(value=self.operation_kind, _type=self.type)


class PayerInnChecker(BaseChecker):
    def __init__(self, payer_inn: Inn, payer_status: str, for_third_face: bool, _type: PaymentType) -> None:
        self.payer_inn = payer_inn
        self.payer_status = payer_status
        self.for_third_face = for_third_face
        self.type = _type

    def check(self) -> None:
        validate_payer_inn(
            value=self.payer_inn,
            _type=self.type,
            payer_status=self.payer_status,
            for_third_face=self.for_third_face,
        )


class UinChecker(BaseChecker):
    def __init__(self, uin: str, payer_inn: Inn, payer_status: str, _type: PaymentType) -> None:
        self.uin = uin
        self.payer_inn = payer_inn
        self.payer_status = payer_status
        self.type = _type

    def check(self) -> None:
        validate_uin(
            value=self.uin,
            _type=self.type,
            payer_inn=self.payer_inn,
            payer_status=self.payer_status,
        )


class PurposeChecker(BaseChecker):
    def __init__(self, purpose: str, _type: PaymentType) -> None:
        self.purpose = purpose
        self.type = _type

    def check(self) -> None:
        validate_purpose(value=self.purpose, _type=self.type)
