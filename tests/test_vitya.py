import pytest
from pydantic import BaseModel, ValidationError as PydanticValidationError

from vitya import (
    ValidationError as VityaValidationError,
    validate_bic,
    validate_inn,
    validate_inn_ip,
    validate_inn_jur,
    validate_kpp,
    validate_ogrn,
    validate_ogrnip,
    validate_oktmo,
    validate_snils,
)
from vitya.pydantic_fields import (
    Bic,
    Inn,
    InnIp,
    InnJur,
    Kpp,
    Ogrn,
    OgrnIp,
    Oktmo,
    Snils,
)


class InnModel(BaseModel):
    inn: Inn


class InnModelIp(BaseModel):
    inn: InnIp


class InnModelJur(BaseModel):
    inn: InnJur


class KppModel(BaseModel):
    kpp: Kpp


class BicModel(BaseModel):
    bic: Bic


class OgrnModel(BaseModel):
    ogrn: Ogrn


class OgrnIpModel(BaseModel):
    ogrnip: OgrnIp


class SnilsModel(BaseModel):
    snils: Snils


class OktmoModel(BaseModel):
    oktmo: Oktmo


@pytest.mark.parametrize('inn', [
    '3664069397', '302502032671', '7707083893', '7703206417', '771002344404'
])
def test_valid_inn(inn):
    """No exception raise"""
    assert validate_inn(inn) is None

    inn_model = InnModel(inn=inn)
    assert inn_model.inn == inn


@pytest.mark.parametrize('inn', [
    '469933069430', '368332974449', '298410962506', '686899030369', '097289845404'
])
def test_valid_inn_ip(inn):
    assert validate_inn_ip(inn) is None

    inn_model_ip = InnModelIp(inn=inn)
    assert inn_model_ip.inn == inn

    with pytest.raises(PydanticValidationError):
        InnModelJur(inn=inn)


@pytest.mark.parametrize('inn', [
    '9267145148', '5302008630', '6524062615', '0207895252', '0990471741'
])
def test_valid_inn_jur(inn):
    assert validate_inn_jur(inn) is None

    inn_model_jur = InnModelJur(inn=inn)
    assert inn_model_jur.inn == inn

    with pytest.raises(PydanticValidationError):
        InnModelIp(inn=inn)


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

    with pytest.raises(PydanticValidationError):
        InnModelIp(inn=inn)

    with pytest.raises(PydanticValidationError):
        InnModelJur(inn=inn)


@pytest.mark.parametrize('kpp', [
    '616401001', '770943002', '7709AB002', '320143522', '704601307'
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
        KppModel(kpp=kpp)


@pytest.mark.parametrize('bic', [
    '044525901', '043002717', '046577964', '040349758', '041806647'
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
        BicModel(bic=bic)


@pytest.mark.parametrize('ogrn', [
    '1027700132195', '1037700013020', '316784700262702', '304500116000157', '1076935620520'
])
def test_valid_ogrn(ogrn):
    """No exception raise"""
    assert validate_ogrn(ogrn) is None

    ogrn_model = OgrnModel(ogrn=ogrn)
    assert ogrn_model.ogrn == ogrn


@pytest.mark.parametrize('ogrnip', [
    '304051927964808', '314057243354856', '307870729546242', '312550098407541', '308633624812989'
])
def test_valid_ogrnip(ogrnip):
    """No exception raise"""
    assert validate_ogrnip(ogrnip) is None

    ogrnip_model = OgrnIpModel(ogrnip=ogrnip)
    assert ogrnip_model.ogrnip == ogrnip


@pytest.mark.parametrize('ogrnip', [
    '1076935620520', '5122703513136', '5081268440446', '5063675362394'
])
def test_wrong_ogrnip(ogrnip):
    with pytest.raises(PydanticValidationError):
        OgrnIpModel(ogrnip=ogrnip)


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

    with pytest.raises(PydanticValidationError):
        OgrnIpModel(ogrnip=ogrn)


@pytest.mark.parametrize('snils', [
    '11223344595',
    '21647164763',
    '47789365577',
    '93149947849',
    '58966302961'
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
    '216-471-647 60',
    '00000000000'
])
def test_wrong_snils(snils):
    with pytest.raises(VityaValidationError):
        validate_snils(snils)

    with pytest.raises(PydanticValidationError):
        SnilsModel(snils=snils)


@pytest.mark.parametrize('oktmo', [
    '69654000',
    '69701000001',
    '98603170051',
    '78623427116',
    '66614465117'
])
def test_valid_oktmo(oktmo):
    """No exception raise"""
    assert validate_oktmo(oktmo) is None

    oktmo_model = OktmoModel(oktmo=oktmo)
    assert oktmo_model.oktmo == oktmo


@pytest.mark.parametrize('oktmo', [
    None,
    '',
    69654000,
    '69154000',
    '69701000000',
    '69 701 000 001'
])
def test_wrong_oktmo(oktmo):
    with pytest.raises(VityaValidationError):
        validate_oktmo(oktmo)

    with pytest.raises(PydanticValidationError):
        OktmoModel(oktmo=oktmo)
