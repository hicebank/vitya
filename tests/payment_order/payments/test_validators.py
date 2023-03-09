from typing import Optional, Type

import pytest

from vitya.payment_order.errors import NumberValidationLenError
from vitya.payment_order.payments.validators import validate_number


@pytest.mark.parametrize(
    'value, exception, expected_value',
    [
        (
            '000001',
            None,
            '000001',
        ),
        (
            '0000011',
            NumberValidationLenError,
            None,
        ),
    ]
)
def test_validate_number(
    value: str,
    exception: Optional[Type[Exception]],
    expected_value: str
) -> None:
    if exception:
        with pytest.raises(exception):
            validate_number(value=value)
    else:
        assert validate_number(value=value) == expected_value
