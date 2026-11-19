from typing import NewType, Optional, Tuple

import pytest
from pydantic import BaseModel, Field, ValidationError
from typing_extensions import Annotated

from tests.helpers import first_validation_cause
from vitya.payment_order.enums import PaymentType
from vitya.payment_order.errors import (
    OperationKindValidationBudgetValueError,
    PurposeValidationValueEmptyErrorForNonFNS,
)
from vitya.payment_order.fields import Amount, ForThirdPerson, OperationKind, Purpose
from vitya.payment_order.payments.checkers import BaseModelChecker
from vitya.pydantic_fields import INN

PYDANTIC_V2 = hasattr(BaseModel, 'model_validate')


@pytest.mark.parametrize('empty', ['0', '', None])
def test_nullable_annotated_identifier(empty):
    class Model(BaseModel):
        inn: Optional[Annotated[INN, Field(description='ИНН')]] = None

    assert Model(inn=empty).inn is None


def test_annotated_purpose_runs_payment_checker():
    class Payment(BaseModelChecker):
        purpose: Optional[Annotated[Purpose, Field(description='Назначение')]] = None
        payment_type: PaymentType

    with pytest.raises(ValidationError) as error:
        Payment(purpose=None, payment_type=PaymentType.IP)
    assert isinstance(first_validation_cause(error.value).errors[0], PurposeValidationValueEmptyErrorForNonFNS)


def test_newtype_runs_operation_kind_checker():
    Kind = NewType('Kind', OperationKind)
    NestedKind = NewType('NestedKind', Kind)

    class Payment(BaseModelChecker):
        operation_kind: Optional[NestedKind]
        payment_type: PaymentType

    with pytest.raises(ValidationError) as error:
        Payment(operation_kind='03', payment_type=PaymentType.FNS)
    assert isinstance(first_validation_cause(error.value).errors[0], OperationKindValidationBudgetValueError)
    assert Payment(operation_kind='01', payment_type=PaymentType.FNS).operation_kind == '01'


def test_omitted_optional_preserves_payment_rules():
    class Payment(BaseModelChecker):
        purpose: Optional[Purpose]
        other: Optional[str] = Field(...)
        payment_type: PaymentType

    payment = Payment(other=None, payment_type=PaymentType.FNS)
    assert payment.purpose is None
    with pytest.raises(ValidationError) as missing:
        Payment(payment_type=PaymentType.FNS)
    assert [e['loc'] for e in missing.value.errors()] == [('other',)]
    with pytest.raises(ValidationError) as invalid:
        Payment(other=None, payment_type=PaymentType.IP)
    assert isinstance(first_validation_cause(invalid.value).errors[0], PurposeValidationValueEmptyErrorForNonFNS)
    schema = Payment.model_json_schema() if PYDANTIC_V2 else Payment.schema()
    assert set(schema['required']) == {'other', 'payment_type'}


def test_mixed_optional_in_reverse_order():
    class Model(BaseModel):
        pair: Tuple[Optional[Annotated[INN, Field(description='ИНН')]], INN]

    assert Model(pair=('0', '3664069397')).pair == (None, '3664069397')
    with pytest.raises(ValidationError) as caught:
        Model(pair=('0', '0'))
    assert [e['loc'] for e in caught.value.errors()] == [('pair', 1)]


@pytest.mark.skipif(not PYDANTIC_V2, reason='PydanticCustomError is a Pydantic 2 API')
def test_combined_errors_preserve_service_code_message_and_context():
    from pydantic import field_validator
    from pydantic_core import PydanticCustomError

    class Payment(BaseModelChecker):
        amount: int
        flag: ForThirdPerson
        operation_kind: OperationKind
        payment_type: PaymentType

        @field_validator('amount')
        @classmethod
        def check_limit(cls, value):
            raise PydanticCustomError('greater_than', 'Сумма вне лимита {limit}', {'limit': 100})

    values = dict(amount=110, flag=1, payment_type=PaymentType.FNS)
    with pytest.raises(ValidationError) as fields:
        Payment(operation_kind='01', **values)
    with pytest.raises(ValidationError) as combined:
        Payment(operation_kind='03', **values)
    details = combined.value.errors()
    assert details[:-1] == fields.value.errors()
    assert [(e['type'], e['msg']) for e in details[:-1]] == [
        ('greater_than', 'Сумма вне лимита 100'),
        ('bool_type', 'value is not a valid boolean'),
    ]
    assert isinstance(details[-1]['ctx']['error'].errors[0], OperationKindValidationBudgetValueError)


def test_rejected_assignment_preserves_payment():
    class Payment(BaseModelChecker, validate_assignment=True):
        operation_kind: OperationKind = OperationKind('01')
        payment_type: PaymentType

    payment = Payment(payment_type=PaymentType.FNS)
    with pytest.raises(ValidationError) as error:
        payment.operation_kind = '03'
    assert isinstance(first_validation_cause(error.value).errors[0], OperationKindValidationBudgetValueError)
    assert payment.operation_kind == '01'
    assert (payment.model_fields_set if PYDANTIC_V2 else payment.__fields_set__) == {'payment_type'}
    payment.operation_kind = '02'
    assert payment.operation_kind == '02'


def test_missing_field_keeps_independent_defaulted_rule():
    calls = []

    def default_kind():
        calls.append('kind')
        return OperationKind('03')

    class Payment(BaseModelChecker):
        amount: Amount
        operation_kind: OperationKind = Field(default_factory=default_kind)
        payment_type: PaymentType = PaymentType.FNS

    with pytest.raises(ValidationError) as caught:
        Payment()
    details = caught.value.errors()
    assert [detail['loc'] for detail in details] == [('amount',), () if PYDANTIC_V2 else ('__root__',)]
    assert calls == ['kind']


@pytest.mark.skipif(not PYDANTIC_V2, reason='Pydantic 2 field validators and JSON validation')
def test_nested_checker_uses_validated_alias_once():
    from pydantic import field_validator

    calls = []

    class Child(BaseModelChecker):
        amount: Amount
        operation_kind: OperationKind = Field(alias='kind')
        payment_type: PaymentType

        @field_validator('operation_kind')
        @classmethod
        def replace_kind(cls, kind):
            calls.append(kind)
            return OperationKind('03')

    class Parent(BaseModelChecker):
        child: Child
        quantity: int

    with pytest.raises(ValidationError) as caught:
        Parent.model_validate_json('{"child":{"amount":"-1","kind":"01","payment_type":"fns"},"quantity":"wrong"}')
    details = caught.value.errors()
    assert [detail['loc'] for detail in details] == [('child', 'amount'), ('child',), ('quantity',)]
    assert isinstance(details[1]['ctx']['error'].errors[0], OperationKindValidationBudgetValueError)
    assert calls == ['01']
