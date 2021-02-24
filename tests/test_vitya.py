import pytest
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from vitya import ValidationError as VityaValidationError
from vitya import validate_bic, validate_inn, validate_kpp, validate_ogrn
from vitya.pydantic_fields import Bic, Inn, Kpp, Ogrn, Snils
from vitya.validators import validate_snils


class InnModel(BaseModel):
    inn: Inn


class KppModel(BaseModel):
    kpp: Kpp


class BicModel(BaseModel):
    bic: Bic


class OgrnModel(BaseModel):
    ogrn: Ogrn


class SnilsModel(BaseModel):
    snils: Snils


@pytest.mark.parametrize('inn', [
    '3664069397', '302502032671', '7707083893', '7703206417', '771002344404'
])
def test_valid_inn(inn):
    """No exception raise"""
    assert validate_inn(inn) is None

    inn_model = InnModel(inn=inn)
    assert inn_model.inn == inn


@pytest.mark.parametrize('inn', [
    None,           # can't be None
    '',
    3664069397,     # can't be nothing than str
    302502032671,
    '770708389',    # should be size of 10 or 12 chars
    '77100234440',
    '3664069398',   # wrong checksums
    '302502032672',
    '302502032681'
    '36640A9397'    # don't match regexp
])
def test_wrong_inn(inn):
    with pytest.raises(VityaValidationError):
        validate_inn(inn)

    with pytest.raises(PydanticValidationError):
        InnModel(inn=inn)


@pytest.mark.parametrize('kpp', [
    '616401001', '770943002', '7709AB002'
])
def test_valid_kpp(kpp):
    """No exception raise"""
    assert validate_kpp(kpp) is None

    kpp_model = KppModel(kpp=kpp)
    assert kpp_model.kpp == kpp


@pytest.mark.parametrize('kpp', [
    None,          # can't be None
    '',
    616401001,     # can't be nothing than str
    770943002,
    '77070838',    # should be size of 9 chars
    '77100234440',
    '7709ABС02'    # don't match regexp
])
def test_wrong_kpp(kpp):
    with pytest.raises(VityaValidationError):
        validate_kpp(kpp)

    with pytest.raises(PydanticValidationError):
        InnModel(kpp=kpp)


@pytest.mark.parametrize('bic', [
    '044525901', '043002717'
])
def test_valid_bic(bic):
    """No exception raise"""
    assert validate_bic(bic) is None

    bic_model = BicModel(bic=bic)
    assert bic_model.bic == bic


@pytest.mark.parametrize('bic', [
    None,          # can't be None
    '',
    770943002,     # can't be nothing than str
    '04452590',    # should be size of 9 chars
    '0445259011',
    '034525901'    # don't match regexp
    '04452A901'
])
def test_wrong_bic(bic):
    with pytest.raises(VityaValidationError):
        validate_bic(bic)

    with pytest.raises(PydanticValidationError):
        InnModel(bic=bic)


@pytest.mark.parametrize('ogrn', [
    '1027700132195', '1037700013020', '316784700262702', '304500116000157'
])
def test_valid_ogrn(ogrn):
    """No exception raise"""
    assert validate_ogrn(ogrn) is None

    ogrn_model = OgrnModel(ogrn=ogrn)
    assert ogrn_model.ogrn == ogrn


@pytest.mark.parametrize('ogrn', [
    None,          # can't be None
    '',
    1027700132195,     # can't be nothing than str
    '102770013219',    # should be size of 13 or 15 chars
    '10377000130200',
    '10277001321955',
    '1027A00132195'    # don't match regexp
    '0027700132195',
    '1027700132196',    # wrong last digit
    '1037700013021'
    '304500116000158',
    '316784700262701'
])
def test_wrong_ogrn(ogrn):
    with pytest.raises(VityaValidationError):
        validate_ogrn(ogrn)

    with pytest.raises(PydanticValidationError):
        OgrnModel(ogrn=ogrn)


@pytest.mark.parametrize('snils', [
    '112-233-445 95'
])
def test_valid_snils(snils):
    """No exception raise"""
    assert validate_snils(snils) is None

    snils_model = SnilsModel(snils=snils)
    assert snils_model.snils == snils


@pytest.mark.parametrize('snils', [
    None,
    '',
    11223344595,
    '12-233-445 955',
    '12-233-445 9',
    '12-233-445-95',
    '12-233-44595',
    '12-233-445 96',
])
def test_wrong_snils(snils):
    with pytest.raises(VityaValidationError):
        validate_snils(snils)

    with pytest.raises(PydanticValidationError):
        SnilsModel(snils=snils)
