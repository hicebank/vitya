import pytest

from vitya import validate_inn, ValidationError


@pytest.mark.parametrize("inn", [
    "3664069397", "302502032671", "7707083893", "7703206417", "771002344404"
])
def test_valid_inn(inn):
    """No exception raise"""
    assert validate_inn(inn) is None


@pytest.mark.parametrize("inn", [
    None,           # inn can't be None
    "",
    3664069397,     # inn can't be nothing than str
    302502032671,
    "770708389",    # inn should be size of 10 or 12 chars
    "77100234440",
    "3664069398",   # wrong checksums
    "302502032672",
    "302502032681"
])
def test_wrong_inn(inn):
    with pytest.raises(ValidationError):
        validate_inn(inn)
