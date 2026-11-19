from decimal import Decimal
from typing import List, Optional, Tuple

import pytest
from pydantic import BaseModel, ValidationError

from tests.helpers import first_validation_cause
from vitya._pydantic import PYDANTIC_V2
from vitya.payment_order.fields import Amount, ForThirdPerson
from vitya.payment_order.payments.checkers import BaseChecker, BaseModelChecker
from vitya.pydantic_fields import INN, Nullable


class Identifiers(BaseModel):
    required: INN
    nullable: Optional[INN] = None
    items: List[Optional[INN]]
    pair: Tuple[INN, Nullable[INN]]


@pytest.mark.parametrize('empty', ['', '0', None])
def test_nullable_identifiers(empty):
    model = Identifiers(required='3664069397', nullable=empty, items=[empty], pair=('3664069397', empty))
    assert model.nullable is None
    assert model.items == [None]
    assert model.pair == ('3664069397', None)
    with pytest.raises(ValidationError) as error:
        Identifiers(required=empty, items=[], pair=(empty, None))
    assert [item['loc'] for item in error.value.errors()] == [('required',), ('pair', 0)]


def test_invalid_identifier_keeps_its_field_and_message():
    with pytest.raises(ValidationError) as error:
        Identifiers(required='abcdef', items=[], pair=('3664069397', None))
    detail, = error.value.errors()
    assert detail['loc'] == ('required',)
    with pytest.raises(ValueError) as domain_error:
        INN('abcdef')
    assert detail['msg'] == str(domain_error.value)


@pytest.mark.skipif(not PYDANTIC_V2, reason='TypeAdapter is a Pydantic 2 API')
def test_standalone_nullable_adapter():
    from pydantic import TypeAdapter

    assert TypeAdapter(Nullable[INN]).validate_python('0') is None
    with pytest.raises(ValidationError):
        TypeAdapter(INN).validate_python('0')
    with pytest.raises(ValidationError):
        TypeAdapter(Nullable[INN]).validate_python('abcdef')


@pytest.mark.skipif(not PYDANTIC_V2, reason='Pydantic 2 JSON schema and serialization')
def test_payment_field_json_round_trip():
    class Payment(BaseModel):
        amount: Amount
        third_person: ForThirdPerson

    schema = Payment.model_json_schema(mode='serialization')
    assert schema['properties']['third_person']['type'] == 'boolean'
    payment = Payment.model_validate_json('{"amount":"0.10","third_person":false}')
    assert type(payment.amount) is Amount
    assert payment.amount == Decimal('0.10')
    assert payment.model_dump(mode='json') == {'amount': '0.10', 'third_person': False}
    with pytest.raises(ValidationError):
        Payment(amount='0.10', third_person=1)


def test_multiple_checker_errors_keep_order():
    class First(BaseChecker):
        def check(self):
            raise ValueError('first')

    class Second(BaseChecker):
        def check(self):
            raise ValueError('second')

    class Payment(BaseModelChecker):
        __extra_wired_checkers__ = [(First, []), (Second, [])]

    with pytest.raises(ValidationError) as error:
        Payment()
    assert [str(e) for e in first_validation_cause(error.value).errors] == ['first', 'second']
