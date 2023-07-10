from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, ClassVar, Dict, List, Sequence, Tuple, Type, AbstractSet, DefaultDict, Mapping, Optional, \
    get_type_hints, get_origin, Union

from pydantic import BaseModel, root_validator
from pydantic.fields import ModelField

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
    check_cbc,
    check_document_date,
    check_document_number,
    check_oktmo,
    check_operation_kind,
    check_receiver_account,
    check_receiver_inn,
    check_receiver_kpp,
    check_payer_inn,
    check_payer_kpp,
    check_payer_status,
    check_payment_type_and_for_third_person,
    check_purpose,
    check_reason,
    check_tax_period,
    check_uin,
)
from vitya.pydantic_fields import BIC, INN, KPP, OKTMO


class CheckerError(ValueError):
    def __init__(self, errors: Sequence[Exception]):
        self._errors = errors

    @property
    def errors(self) -> Sequence[Exception]:
        return self._errors


class BaseChecker(ABC):
    @abstractmethod
    def check(self) -> None:  # pragma: no cover
        pass


class ReceiverAccountChecker(BaseChecker):
    def __init__(self, account_number: AccountNumber, bic: BIC, payment_type: PaymentType) -> None:
        self.account_number = account_number
        self.bic = bic
        self.payment_type = payment_type

    def check(self) -> None:
        check_receiver_account(value=self.account_number, payment_type=self.payment_type, receiver_bic=self.bic)


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
        for_third_person: bool,
        payment_type: PaymentType
    ) -> None:
        self.payer_inn = payer_inn
        self.payer_status = payer_status
        self.for_third_person = for_third_person
        self.payment_type = payment_type

    def check(self) -> None:
        check_payer_inn(
            value=self.payer_inn,
            payment_type=self.payment_type,
            payer_status=self.payer_status,
            for_third_person=self.for_third_person
        )


class UINChecker(BaseChecker):
    def __init__(
        self,
        uin: UIN,
        receiver_account: AccountNumber,
        payer_inn: INN,
        payer_status: PayerStatus,
        payment_type: PaymentType,
    ) -> None:
        self.uin = uin
        self.receiver_account = receiver_account
        self.payer_inn = payer_inn
        self.payer_status = payer_status
        self.payment_type = payment_type

    def check(self) -> None:
        check_uin(
            value=self.uin,
            receiver_account=self.receiver_account,
            payment_type=self.payment_type,
            payer_status=self.payer_status,
            payer_inn=self.payer_inn,
        )


class PurposeChecker(BaseChecker):
    def __init__(self, purpose: Purpose, payment_type: PaymentType, payer_account: AccountNumber) -> None:
        self.purpose = purpose
        self.payment_type = payment_type
        self.payer_account = payer_account

    def check(self) -> None:
        check_purpose(value=self.purpose, payment_type=self.payment_type, payer_account=self.payer_account)


class ReceiverINNChecker(BaseChecker):
    def __init__(
        self,
        receiver_inn: INN,
        payment_type: PaymentType
    ) -> None:
        self.receiver_inn = receiver_inn
        self.payment_type = payment_type

    def check(self) -> None:
        check_receiver_inn(value=self.receiver_inn, payment_type=self.payment_type)


class PayerStatusChecker(BaseChecker):
    def __init__(
        self,
        payer_status: PayerStatus,
        payment_type: PaymentType,
        for_third_person: bool,
    ) -> None:
        self.payer_status = payer_status
        self.payment_type = payment_type
        self.for_third_person = for_third_person

    def check(self) -> None:
        check_payer_status(
            value=self.payer_status,
            payment_type=self.payment_type,
            for_third_person=self.for_third_person
        )


class PaymentTypeAndForThirdPersonChecker(BaseChecker):
    def __init__(
        self,
        payment_type: PaymentType,
        for_third_person: bool,
    ) -> None:
        self.payment_type = payment_type
        self.for_third_person = for_third_person

    def check(self) -> None:
        check_payment_type_and_for_third_person(
            payment_type=self.payment_type,
            for_third_person=self.for_third_person
        )


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


class ReceiverKPPChecker(BaseChecker):
    def __init__(
        self,
        receiver_kpp: KPP,
        payment_type: PaymentType,
    ) -> None:
        self.receiver_kpp = receiver_kpp
        self.payment_type = payment_type

    def check(self) -> None:
        check_receiver_kpp(value=self.receiver_kpp, payment_type=self.payment_type)


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
        receiver_account: AccountNumber,
        uin: UIN,
        payer_inn: INN,
    ) -> None:
        self.document_number = document_number
        self.payment_type = payment_type
        self.reason = reason
        self.payer_status = payer_status
        self.receiver_account = receiver_account
        self.uin = uin
        self.payer_inn = payer_inn

    def check(self) -> None:
        check_document_number(
            value=self.document_number,
            payment_type=self.payment_type,
            reason=self.reason,
            payer_status=self.payer_status,
            receiver_account=self.receiver_account,
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


WiredChecker = Tuple[Type[BaseChecker], Sequence[str]]


class BaseModelChecker(BaseModel):
    __extra_checkers__: ClassVar[Sequence[WiredChecker]] = []
    __auto_checkers__: ClassVar[Sequence[Type[BaseChecker]]] = [
        # AccountBicChecker
        ReceiverAccountChecker,
        OperationKindChecker,
        PayerINNChecker,
        UINChecker,
        PurposeChecker,
        ReceiverINNChecker,
        PayerStatusChecker,
        PaymentTypeAndForThirdPersonChecker,
        PayerKPPChecker,
        ReceiverKPPChecker,
        CBCChecker,
        OKTMOChecker,
        ReasonChecker,
        TaxPeriodChecker,
        DocumentNumberChecker,
        DocumentDateChecker,
    ]
    __auto_checkers__ = []
    __excluded_auto_checkers__: ClassVar[AbstractSet[Type[BaseChecker]]] = {}
    __wire_auto_checkers__: ClassVar[bool] = True  # disable to use only __extra_checkers__

    __wired_checkers__: ClassVar[Sequence[WiredChecker]]  # this value is computed at __init_subclass__

    def __init_subclass__(cls, **kwargs: Dict[str, Any]) -> None:  # pragma: no cover
        # built error
        errors = []
        for checker, fields in cls.__extra_checkers__:
            wild_fields = set(fields) - cls.__fields__.keys()
            if wild_fields:
                errors.append(f'Checker {checker} require unknown model fields {wild_fields}')
        if errors:
            raise ValueError(errors)

        cls.__wired_checkers__ = list(cls.__extra_checkers__) + list(cls._wire_auto_checkers())

    @classmethod
    def _wire_auto_checkers(cls) -> Sequence[WiredChecker]:
        if not cls.__wire_auto_checkers__:
            return []
        auto_checkers = [
            checker_cls
            for checker_cls in cls.__auto_checkers__
            if checker_cls not in cls.__excluded_auto_checkers__
        ]
        type_to_fields: DefaultDict[Any, List[ModelField]] = defaultdict(list)
        for field in cls.__fields__.values():
            type_to_fields[field.type_].append(field)

        result: List[WiredChecker] = []
        for checker_cls in auto_checkers:
            wired_checker = cls._wire_checker(type_to_fields, checker_cls)
            if wired_checker is not None:
                result.append(wired_checker)

        return result

    @classmethod
    def _wire_checker(
        cls,
        type_to_fields: Mapping[Any, Sequence[ModelField]],
        checker_cls: Type[BaseChecker],
    ) -> Optional[WiredChecker]:
        parameters = get_type_hints(checker_cls.__init__)  # by default get_type_hints strips Annotated
        field_names: List[str] = []
        for parameter in parameters[1:].values():  # skip self
            try:
                fields = type_to_fields[parameter.annotation]
            except KeyError:
                return None
            if len(fields) == 1:
                field_names.append(fields[0].name)
            raise ValueError(
                f'{checker_cls} requires field with type {parameter.annotation},'
                f' but there are several candidates {[field.name for field in fields]}'
            )

        return checker_cls, field_names

    @classmethod
    def _get_matching_fields_by_type(
        cls,
        type_to_fields: Mapping[Any, Sequence[ModelField]],
        tp: Any,
    ) -> Sequence[ModelField]:
        if get_origin(tp) != Union:
            return type_to_fields.get(tp, [])

        union_args = set(tp.__args__)
        result: List[ModelField] = []
        for field_type, fields in type_to_fields.items():
            if get_origin(field_type) != Union:
                if field_type in union_args:
                    result.extend(fields)
            elif set(field_type.__args__).issubset(union_args):
                result.extend(fields)
        return result

    @root_validator(pre=False)
    def run_checkers(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        errors = []
        for checker, fields_names in cls.__wired_checkers__:
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

