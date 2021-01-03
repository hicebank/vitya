import pytest

from vitya import validate_inn, ValidationError, validate_kpp, validate_bic, validate_ogrn


@pytest.mark.parametrize("inn", [
    "3664069397", "302502032671", "7707083893", "7703206417", "771002344404"
])
def test_valid_inn(inn):
    """No exception raise"""
    assert validate_inn(inn) is None


@pytest.mark.parametrize("inn", [
    None,           # can't be None
    "",
    3664069397,     # can't be nothing than str
    302502032671,
    "770708389",    # should be size of 10 or 12 chars
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
    None,          # can't be None
    "",
    616401001,     # can't be nothing than str
    770943002,
    "77070838",    # should be size of 9 chars
    "77100234440",
    "7709ABС02"    # don't match regexp
])
def test_wrong_kpp(kpp):
    with pytest.raises(ValidationError):
        validate_kpp(kpp)


@pytest.mark.parametrize("bic", [
    "044525901", "043002717"
])
def test_valid_bic(bic):
    """No exception raise"""
    assert validate_bic(bic) is None


@pytest.mark.parametrize("bic", [
    None,          # can't be None
    "",
    770943002,     # can't be nothing than str
    "04452590",    # should be size of 9 chars
    "0445259011",
    "034525901"    # don't match regexp
    "04452A901"
])
def test_wrong_bic(bic):
    with pytest.raises(ValidationError):
        validate_bic(bic)


@pytest.mark.parametrize("ogrn", [
    "1027700132195", "1037700013020"
])
def test_valid_ogrn(ogrn):
    """No exception raise"""
    assert validate_ogrn(ogrn) is None


@pytest.mark.parametrize("ogrn", [
    None,          # can't be None
    "",
    1027700132195,     # can't be nothing than str
    "102770013219",    # should be size of 13 chars
    "10277001321955",
    "1027A00132195"    # don't match regexp
    "0027700132195"
])
def test_wrong_ogrn(ogrn):
    with pytest.raises(ValidationError):
        validate_ogrn(ogrn)
