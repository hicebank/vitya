from abc import ABC, abstractmethod
from collections import defaultdict
from typing import (
    AbstractSet,
    Any,
    ClassVar,
    DefaultDict,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    get_type_hints,
)

from pydantic import BaseModel, root_validator
from pydantic.fields import ModelField

from vitya.payment_order.enums import PaymentType
from vitya.payment_order.fields import (
    CBC,
    UIN,
    DocumentDate,
    DocumentNumber,
    ForThirdPerson,
    OperationKind,
    PayerINN,
    PayerKPP,
    PayerStatus,
    Purpose,
    Reason,
    ReceiverAccountNumber,
    ReceiverBIC,
    ReceiverINN,
    ReceiverKPP,
    TaxPeriod,
)
from vitya.payment_order.payments.checks import (
    check_cbc,
    check_document_date,
    check_document_date_with_reason,
    check_document_number,
    check_oktmo,
    check_oktmo_with_payer_status,
    check_oktmo_with_receiver_account_number,
    check_operation_kind,
    check_payer_inn,
    check_payer_inn_with_uin_and_receiver_account,
    check_payer_kpp,
    check_payer_status,
    check_payment_type_and_for_third_person,
    check_purpose,
    check_purpose_for_third_person,
    check_reason,
    check_receiver_account,
    check_receiver_account_with_payment_type,
    check_receiver_account_with_payment_type_and_payer_status,
    check_receiver_inn,
    check_receiver_kpp,
    check_tax_period,
    check_uin,
)
from vitya.pydantic_fields import OKTMO
from vitya.typing_helpers import is_union, normalize_type


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
    def __init__(self, account_number: ReceiverAccountNumber, bic: ReceiverBIC, payment_type: PaymentType) -> None:
        self.account_number = account_number
        self.bic = bic
        self.payment_type = payment_type

    def check(self) -> None:
        check_receiver_account(value=self.account_number, payment_type=self.payment_type, receiver_bic=self.bic)


class ReceiverAccountCheckerWithPaymentType(BaseChecker):
    def __init__(self, account_number: ReceiverAccountNumber, payment_type: PaymentType) -> None:
        self.account_number = account_number
        self.payment_type = payment_type

    def check(self) -> None:
        check_receiver_account_with_payment_type(value=self.account_number, payment_type=self.payment_type)


class ReceiverAccountCheckerWithPaymentTypeAndPayerStatus(BaseChecker):
    def __init__(
        self,
        account_number: ReceiverAccountNumber,
        payment_type: PaymentType,
        payer_status: Optional[PayerStatus]
    ) -> None:
        self.account_number = account_number
        self.payment_type = payment_type
        self.payer_status = payer_status

    def check(self) -> None:
        check_receiver_account_with_payment_type_and_payer_status(
            value=self.account_number,
            payment_type=self.payment_type,
            payer_status=self.payer_status,
        )


class OperationKindChecker(BaseChecker):
    def __init__(self, operation_kind: OperationKind, payment_type: PaymentType) -> None:
        self.operation_kind = operation_kind
        self.payment_type = payment_type

    def check(self) -> None:
        check_operation_kind(value=self.operation_kind, payment_type=self.payment_type)


class PayerINNChecker(BaseChecker):
    def __init__(
        self,
        payer_inn: Optional[PayerINN],
        payer_status: Optional[PayerStatus],
        for_third_person: ForThirdPerson,
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
            for_third_person=self.for_third_person,
        )


class PayerINNWithUinAndReceiverAccountChecker(BaseChecker):
    def __init__(
        self,
        payer_inn: Optional[PayerINN],
        payer_status: Optional[PayerStatus],
        receiver_account: Optional[ReceiverAccountNumber],
        uin: Optional[UIN],
        payment_type: PaymentType
    ) -> None:
        self.payer_inn = payer_inn
        self.payer_status = payer_status
        self.payment_type = payment_type
        self.receiver_account = receiver_account
        self.uin = uin

    def check(self) -> None:
        check_payer_inn_with_uin_and_receiver_account(
            value=self.payer_inn,
            payment_type=self.payment_type,
            payer_status=self.payer_status,
            receiver_account=self.receiver_account,
            uin=self.uin,
        )


class UINChecker(BaseChecker):
    def __init__(
        self,
        uin: Optional[UIN],
        receiver_account: ReceiverAccountNumber,
        payer_inn: Optional[PayerINN],
        payer_status: Optional[PayerStatus],
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
    def __init__(
        self,
        purpose: Optional[Purpose],
        payment_type: PaymentType,
    ) -> None:
        self.purpose = purpose
        self.payment_type = payment_type

    def check(self) -> None:
        check_purpose(value=self.purpose, payment_type=self.payment_type)


class ReceiverINNChecker(BaseChecker):
    def __init__(
        self,
        receiver_inn: Optional[ReceiverINN],
        payment_type: PaymentType
    ) -> None:
        self.receiver_inn = receiver_inn
        self.payment_type = payment_type

    def check(self) -> None:
        check_receiver_inn(value=self.receiver_inn, payment_type=self.payment_type)


class PayerStatusChecker(BaseChecker):
    def __init__(
        self,
        payer_status: Optional[PayerStatus],
        payment_type: PaymentType,
        for_third_person: Optional[ForThirdPerson],
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
        for_third_person: ForThirdPerson,
    ) -> None:
        self.payment_type = payment_type
        self.for_third_person = for_third_person

    def check(self) -> None:
        check_payment_type_and_for_third_person(
            payment_type=self.payment_type,
            for_third_person=self.for_third_person
        )


class ForThirdPersonAndPurposeChecker(BaseChecker):
    def __init__(
        self,
        purpose: Optional[Purpose],
        for_third_person: ForThirdPerson,
    ) -> None:
        self.purpose = purpose
        self.for_third_person = for_third_person

    def check(self) -> None:
        check_purpose_for_third_person(
            value=self.purpose,
            for_third_person=self.for_third_person
        )


class PayerKPPChecker(BaseChecker):
    def __init__(
        self,
        payer_kpp: Optional[PayerKPP],
        payment_type: PaymentType,
        payer_inn: Optional[PayerINN],
        payer_status: Optional[PayerStatus],
    ) -> None:
        self.payer_kpp = payer_kpp
        self.payment_type = payment_type
        self.payer_inn = payer_inn
        self.payer_status = payer_status

    def check(self) -> None:
        check_payer_kpp(
            value=self.payer_kpp,
            payment_type=self.payment_type,
            payer_inn=self.payer_inn,
            payer_status=self.payer_status,
        )


class ReceiverKPPChecker(BaseChecker):
    def __init__(
        self,
        receiver_kpp: Optional[ReceiverKPP],
        payment_type: PaymentType,
    ) -> None:
        self.receiver_kpp = receiver_kpp
        self.payment_type = payment_type

    def check(self) -> None:
        check_receiver_kpp(value=self.receiver_kpp, payment_type=self.payment_type)


class CBCChecker(BaseChecker):
    def __init__(
        self,
        cbc: Optional[CBC],
        payment_type: PaymentType,
    ) -> None:
        self.cbc = cbc
        self.payment_type = payment_type

    def check(self) -> None:
        check_cbc(value=self.cbc, payment_type=self.payment_type)


class OKTMOChecker(BaseChecker):
    def __init__(
        self,
        oktmo: Optional[OKTMO],
        payment_type: PaymentType,
    ) -> None:
        self.oktmo = oktmo
        self.payment_type = payment_type

    def check(self) -> None:
        check_oktmo(value=self.oktmo, payment_type=self.payment_type)


class OKTMOWithPayerStatusChecker(BaseChecker):
    def __init__(
        self,
        oktmo: Optional[OKTMO],
        payment_type: PaymentType,
        payer_status: Optional[PayerStatus],
    ) -> None:
        self.oktmo = oktmo
        self.payment_type = payment_type
        self.payer_status = payer_status

    def check(self) -> None:
        check_oktmo_with_payer_status(value=self.oktmo, payment_type=self.payment_type, payer_status=self.payer_status)


class OKTMOWithReceiverAccountNumberChecker(BaseChecker):
    def __init__(
        self,
        oktmo: Optional[OKTMO],
        payment_type: PaymentType,
        receiver_account_number: ReceiverAccountNumber,
    ) -> None:
        self.oktmo = oktmo
        self.payment_type = payment_type
        self.receiver_account_number = receiver_account_number

    def check(self) -> None:
        check_oktmo_with_receiver_account_number(
            value=self.oktmo,
            payment_type=self.payment_type,
            receiver_account_number=self.receiver_account_number
        )


class ReasonChecker(BaseChecker):
    def __init__(
        self,
        reason: Optional[Reason],
        payment_type: PaymentType,
    ) -> None:
        self.reason = reason
        self.payment_type = payment_type

    def check(self) -> None:
        check_reason(value=self.reason, payment_type=self.payment_type)


class TaxPeriodChecker(BaseChecker):
    def __init__(
        self,
        tax_period: Optional[TaxPeriod],
        payment_type: PaymentType,
        payer_status: Optional[PayerStatus],
    ) -> None:
        self.tax_period = tax_period
        self.payment_type = payment_type
        self.payer_status = payer_status

    def check(self) -> None:
        check_tax_period(value=self.tax_period, payment_type=self.payment_type, payer_status=self.payer_status)


class DocumentNumberChecker(BaseChecker):
    def __init__(
        self,
        document_number: Optional[DocumentNumber],
        payment_type: PaymentType,
        reason: Optional[Reason],
        payer_status: Optional[PayerStatus],
        uin: Optional[UIN],
        payer_inn: Optional[PayerINN],
    ) -> None:
        self.document_number = document_number
        self.payment_type = payment_type
        self.reason = reason
        self.payer_status = payer_status
        self.uin = uin
        self.payer_inn = payer_inn

    def check(self) -> None:
        check_document_number(
            value=self.document_number,
            payment_type=self.payment_type,
            reason=self.reason,
            payer_status=self.payer_status,
            uin=self.uin,
            payer_inn=self.payer_inn,
        )


class DocumentDateChecker(BaseChecker):
    def __init__(
        self,
        document_date: Optional[DocumentDate],
        payment_type: PaymentType,
    ) -> None:
        self.document_date = document_date
        self.payment_type = payment_type

    def check(self) -> None:
        check_document_date(value=self.document_date, payment_type=self.payment_type)


class DocumentDateWithReasonChecker(BaseChecker):
    def __init__(
        self,
        document_date: Optional[DocumentDate],
        payment_type: PaymentType,
        reason: Reason,
    ) -> None:
        self.document_date = document_date
        self.payment_type = payment_type
        self.reason = reason

    def check(self) -> None:
        check_document_date_with_reason(value=self.document_date, payment_type=self.payment_type, reason=self.reason)


WiredChecker = Tuple[Type[BaseChecker], Sequence[str]]


class BaseModelChecker(BaseModel):
    __extra_wired_checkers__: ClassVar[Sequence[WiredChecker]] = []
    __auto_checkers__: ClassVar[Sequence[Type[BaseChecker]]] = [
        ReceiverAccountChecker,
        ReceiverAccountCheckerWithPaymentType,
        ReceiverAccountCheckerWithPaymentTypeAndPayerStatus,
        OperationKindChecker,
        PayerINNChecker,
        PayerINNWithUinAndReceiverAccountChecker,
        UINChecker,
        PurposeChecker,
        ReceiverINNChecker,
        PayerStatusChecker,
        PaymentTypeAndForThirdPersonChecker,
        ForThirdPersonAndPurposeChecker,
        PayerKPPChecker,
        ReceiverKPPChecker,
        CBCChecker,
        OKTMOChecker,
        OKTMOWithPayerStatusChecker,
        OKTMOWithReceiverAccountNumberChecker,
        ReasonChecker,
        TaxPeriodChecker,
        DocumentNumberChecker,
        DocumentDateChecker,
        DocumentDateWithReasonChecker,
    ]
    __excluded_auto_checkers__: ClassVar[AbstractSet[Type[BaseChecker]]] = set()
    __wire_auto_checkers__: ClassVar[bool] = True  # disable to use only __extra_wired_checkers__

    __final_wired_checkers__: ClassVar[Sequence[WiredChecker]]  # this value is computed at __init_subclass__

    def __init_subclass__(cls, **kwargs: Dict[str, Any]) -> None:  # pragma: no cover
        # built error
        errors = []
        for checker, fields in cls.__extra_wired_checkers__:
            wild_fields = set(fields) - cls.__fields__.keys()
            if wild_fields:
                errors.append(f'Checker {checker} require unknown model fields {wild_fields}')
        if errors:
            raise ValueError(errors)

        cls.__final_wired_checkers__ = list(cls.__extra_wired_checkers__) + list(cls._wire_auto_checkers())

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
            type_to_fields[normalize_type(field.type_)].append(field)
        type_to_fields.default_factory = None

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
        for param_name, param_type in parameters.items():
            if param_name == 'return':
                continue

            fields = cls._get_matching_fields_by_type(type_to_fields, param_type)
            if len(fields) == 0:
                return None
            elif len(fields) == 1:
                field_names.append(fields[0].name)
            else:
                raise ValueError(
                    f'{checker_cls} requires field with type {param_type},'
                    f' but there are several candidates {[field.name for field in fields]}'
                )

        return checker_cls, field_names

    @classmethod
    def _get_matching_fields_by_type(
        cls,
        type_to_fields: Mapping[Any, Sequence[ModelField]],
        tp: Any,
    ) -> Sequence[ModelField]:
        if not is_union(tp):
            return type_to_fields.get(normalize_type(tp), [])

        union_args = set(tp.__args__)
        result: List[ModelField] = []
        for field_type, fields in type_to_fields.items():
            norm_field_type = normalize_type(field_type)
            if not is_union(norm_field_type):
                if norm_field_type in union_args:
                    result.extend(fields)
            elif set(norm_field_type.__args__).issubset(union_args):
                result.extend(fields)
        return result

    @root_validator(pre=False)
    def run_checkers(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        errors = []
        for checker, fields_names in cls.__final_wired_checkers__:
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
