import pytest

from vitya import validate_inn, ValidationError, validate_kpp


@pytest.mark.parametrize("inn", [
    "3664069397", "302502032671", "7707083893", "7703206417", "771002344404"
])
def test_valid_inn(inn):
    """No exception raise"""
    assert validate_inn(inn) is None


@pytest.mark.parametrize("inn", [
    None,           # inn can't be None
    3664069397,     # inn can't be nothing than str
    302502032671,
    "770708389",    # inn should be size of 10 or 12 chars
    "77100234440",
    "3664069398",   # wrong checksums
    "302502032672",
    "302502032681"
    "36640A9397"    # don't match regexp
])
def test_wrong_inn(inn):
    with pytest.raises(ValidationError):
        validate_inn(inn)


@pytest.mark.parametrize("kpp", [
    "616401001", "770943002", "7709AB002"
])
def test_valid_kpp(kpp):
    """No exception raise"""
    assert validate_kpp(kpp) is None


@pytest.mark.parametrize("kpp", [
    None,          # inn can't be None
    "",
    616401001,     # inn can't be nothing than str
    770943002,
    "77070838",    # inn should be size of 9 chars
    "77100234440",
    "7709ABС02"    # don't match regexp
])
def test_wrong_kpp(kpp):
    with pytest.raises(ValidationError):
        validate_kpp(kpp)
