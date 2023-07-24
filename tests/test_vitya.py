from typing import Optional

import pytest
from pydantic import BaseModel, ValidationError as PydanticValidationError
from pydantic.errors import PydanticValueError

from vitya import (
    ValidationError as VityaValidationError,
    validate_bic,
    validate_inn,
    validate_inn_ip,
    validate_inn_le,
    validate_kpp,
    validate_ogrn,
    validate_ogrnip,
    validate_oktmo,
    validate_snils,
)
from vitya.errors import (
    OKTMOValidationTypeError,
    OKTMOValidationValueError,
    OKTMOValidationValueLenError,
)
from vitya.pydantic_fields import (
    BIC,
    INN,
    INNIP,
    INNLE,
    KPP,
    OGRN,
    OGRNIP,
    OKTMO,
    SNILS,
    FieldMixin,
)


class INNModel(BaseModel):
    inn: INN


class INNIPModel(BaseModel):
    inn: INNIP


class INNLEModel(BaseModel):
    inn: INNLE


class KPPModel(BaseModel):
    kpp: KPP


class BICModel(BaseModel):
    bic: BIC


class OGRNModel(BaseModel):
    ogrn: OGRN


class OGRNIPModel(BaseModel):
    ogrnip: OGRNIP


class SNILSModel(BaseModel):
    snils: SNILS


class OKTMOModel(BaseModel):
    oktmo: OKTMO


@pytest.mark.parametrize(
    'inn', [
        '3664069397', '302502032671', '7707083893', '7703206417', '771002344404'
    ]
)
def test_valid_inn(inn):
    """No exception raise"""
    validate_inn(inn)

    inn_model = INNModel(inn=inn)
    assert inn_model.inn == inn


@pytest.mark.parametrize(
    'inn', [
        '469933069430', '368332974449', '298410962506', '686899030369', '097289845404'
    ]
)
def test_valid_inn_ip(inn):
    validate_inn_ip(inn)

    inn_model_ip = INNIPModel(inn=inn)
    assert inn_model_ip.inn == inn

    with pytest.raises(PydanticValidationError):
        INNLEModel(inn=inn)


@pytest.mark.parametrize(
    'inn', [
        '9267145148', '5302008630', '6524062615', '0207895252', '0990471741'
    ]
)
def test_valid_inn_le(inn):
    validate_inn_le(inn)

    inn_model_le = INNLEModel(inn=inn)
    assert inn_model_le.inn == inn

    with pytest.raises(PydanticValidationError):
        INNIPModel(inn=inn)


@pytest.mark.parametrize(
    'inn', [
        None,  # can't be None
        3664069397,  # can't be nothing than str
        302502032671,
        '770708389',  # should be size of 10 or 12 chars
        '77100234440',
        '3664069398',  # wrong checksums
        '302502032672',
        '302502032681'
        '36640A9397'  # don't match regexp
    ]
)
def test_wrong_inn(inn):
    with pytest.raises(PydanticValueError):
        validate_inn(inn)

    with pytest.raises(PydanticValidationError):
        INNModel(inn=inn)

    with pytest.raises(PydanticValidationError):
        INNIPModel(inn=inn)

    with pytest.raises(PydanticValidationError):
        INNLEModel(inn=inn)


@pytest.mark.parametrize(
    'kpp', [
        '616401001', '770943002', '7709AB002', '320143522', '704601307',
    ]
)
def test_valid_kpp(kpp):
    """No exception raise"""
    validate_kpp(kpp)

    kpp_model = KPPModel(kpp=kpp)
    assert kpp_model.kpp == kpp


@pytest.mark.parametrize(
    'kpp', [
        None,  # can't be None
        616401001,  # can't be nothing than str
        770943002,
        '77070838',  # should be size of 9 chars
        '77100234440',
        '7709ABС02'  # don't match regexp
    ]
)
def test_wrong_kpp(kpp):
    with pytest.raises(PydanticValueError):
        validate_kpp(kpp)

    with pytest.raises(PydanticValidationError):
        KPPModel(kpp=kpp)


@pytest.mark.parametrize(
    'bic', [
        '044525901', '043002717', '046577964', '040349758', '041806647'
    ]
)
def test_valid_bic(bic):
    """No exception raise"""
    validate_bic(bic)

    bic_model = BICModel(bic=bic)
    assert bic_model.bic == bic


@pytest.mark.parametrize(
    'bic', [
        None,  # can't be None
        '',
        770943002,  # can't be nothing than str
        '04452590',  # should be size of 9 chars
        '0445259011',
        '034525901'  # don't match regexp
        '04452A901'
    ]
)
def test_wrong_bic(bic):
    with pytest.raises(PydanticValueError):
        validate_bic(bic)

    with pytest.raises(PydanticValidationError):
        BICModel(bic=bic)


@pytest.mark.parametrize(
    'ogrn', [
        '1027700132195', '1037700013020', '316784700262702', '304500116000157', '1076935620520'
    ]
)
def test_valid_ogrn(ogrn):
    """No exception raise"""
    assert validate_ogrn(ogrn) is None

    ogrn_model = OGRNModel(ogrn=ogrn)
    assert ogrn_model.ogrn == ogrn


@pytest.mark.parametrize(
    'ogrnip', [
        '304051927964808', '314057243354856', '307870729546242', '312550098407541', '308633624812989'
    ]
)
def test_valid_ogrnip(ogrnip):
    """No exception raise"""
    assert validate_ogrnip(ogrnip) is None

    ogrnip_model = OGRNIPModel(ogrnip=ogrnip)
    assert ogrnip_model.ogrnip == ogrnip


@pytest.mark.parametrize(
    'ogrnip', [
        '1076935620520', '5122703513136', '5081268440446', '5063675362394'
    ]
)
def test_wrong_ogrnip(ogrnip):
    with pytest.raises(PydanticValidationError):
        OGRNIPModel(ogrnip=ogrnip)


@pytest.mark.parametrize(
    'ogrn', [
        None,  # can't be None
        '',
        1027700132195,  # can't be nothing than str
        '102770013219',  # should be size of 13 or 15 chars
        '10377000130200',
        '10277001321955',
        '1027A00132195'  # don't match regexp
        '0027700132195',
        '1027700132196',  # wrong last digit
        '1037700013021'
        '304500116000158',
        '316784700262701'
    ]
)
def test_wrong_ogrn(ogrn):
    with pytest.raises(VityaValidationError):
        validate_ogrn(ogrn)

    with pytest.raises(PydanticValidationError):
        OGRNModel(ogrn=ogrn)

    with pytest.raises(PydanticValidationError):
        OGRNIPModel(ogrnip=ogrn)


@pytest.mark.parametrize(
    'snils', [
        '11223344595',
        '21647164763',
        '47789365577',
        '93149947849',
        '58966302961'
    ]
)
def test_valid_snils(snils):
    """No exception raise"""
    assert validate_snils(snils) is None

    snils_model = SNILSModel(snils=snils)
    assert snils_model.snils == snils


@pytest.mark.parametrize(
    'snils', [
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
    ]
)
def test_wrong_snils(snils):
    with pytest.raises(VityaValidationError):
        validate_snils(snils)

    with pytest.raises(PydanticValidationError):
        SNILSModel(snils=snils)


@pytest.mark.parametrize(
    'oktmo', [
        '69654000',
        '69701000001',
        '98603170051',
        '78623427116',
        '66614465117',
    ]
)
def test_valid_oktmo(oktmo):
    """No exception raise"""
    assert validate_oktmo(oktmo) == oktmo

    oktmo_model = OKTMOModel(oktmo=oktmo)
    assert oktmo_model.oktmo == oktmo


@pytest.mark.parametrize(
    'oktmo, error',
    [
        (None, OKTMOValidationTypeError),
        (69654000, OKTMOValidationTypeError),
        ('6965400', OKTMOValidationValueLenError),
        ('69b01000001', OKTMOValidationValueError),
    ]
)
def test_wrong_oktmo(oktmo, error):
    with pytest.raises(error):
        validate_oktmo(oktmo)

    with pytest.raises(PydanticValidationError):
        OKTMOModel(oktmo=oktmo)


class Field(FieldMixin, str):
    @classmethod
    def _validate(cls, value):
        return value if value not in {'', '0'} else None


class TestFieldMixin(BaseModel):
    field: Field


@pytest.mark.parametrize(
    'value',
    ('', '0', None)
)
def test_field_mixin(value: Optional[str]) -> None:
    with pytest.raises(PydanticValidationError):
        TestFieldMixin(field=value)


class TestFieldMixinOptional(BaseModel):
    field: Optional[Field]


@pytest.mark.parametrize(
    'value',
    ('', '0', None)
)
def test_field_mixin_optional(value: Optional[str]) -> None:
    assert TestFieldMixinOptional(field=value).field is None


class TestFieldMixinOptionalWithDefault(BaseModel):
    field: Optional[Field] = '5'


def test_field_mixin_optional_with_default() -> None:
    assert TestFieldMixinOptionalWithDefault().field == '5'


@pytest.mark.parametrize(
    'value',
    ('', '0', None),
)
def test_field_mixin_optional_with_default_with_value(value: Optional[str]) -> None:
    assert TestFieldMixinOptionalWithDefault(field=value).field is None
