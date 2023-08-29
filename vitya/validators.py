import re
from typing import List, Optional

from .errors import (
    BICValidationLenError,
    BICValidationTypeError,
    BICValidationValueDigitsOnlyError,
    INNValidationControlSumError,
    INNValidationDigitsOnlyError,
    INNValidationLenError,
    INNValidationStartsWithZerosError,
    INNValidationTypeError,
    KPPValidationTypeError,
    KPPValidationValueError,
    KPPValidationValueLenError,
    OKTMOValidationTypeError,
    OKTMOValidationValueError,
    OKTMOValidationValueLenError,
)


class ValidationError(ValueError):
    """
    Exception that raises if passed data is invalid
    """
    pass


def _count_inn_checksum(inn: str, coefficients: List[int]) -> int:
    assert len(inn) == len(coefficients)
    n = sum([int(digit) * coef for digit, coef in zip(inn, coefficients)])
    return n % 11 % 10


def validate_inn(inn: str, is_ip: Optional[bool] = None) -> Optional[str]:
    """
    Source:
    https://www.consultant.ru/document/cons_doc_LAW_134082/947eeb5630c9f58cbc6103f0910440cef8eaccac/
    https://ru.wikipedia.org/wiki/%D0%98%D0%B4%D0%B5%D0%BD%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%86%D0%B8%D0%BE%D0%BD%D0%BD%D1%8B%D0%B9_%D0%BD%D0%BE%D0%BC%D0%B5%D1%80_%D0%BD%D0%B0%D0%BB%D0%BE%D0%B3%D0%BE%D0%BF%D0%BB%D0%B0%D1%82%D0%B5%D0%BB%D1%8C%D1%89%D0%B8%D0%BA%D0%B0
    """
    if not isinstance(inn, str):
        raise INNValidationTypeError

    if inn in {'', '0'}:
        return None

    if not re.fullmatch(r'[0-9]+', inn):
        raise INNValidationDigitsOnlyError

    if inn.startswith('00'):
        raise INNValidationStartsWithZerosError

    coefs10 = [2, 4, 10, 3, 5, 9, 4, 6, 8]
    coefs11 = [7] + coefs10
    coefs12 = [3] + coefs11

    if len(inn) == 10 and is_ip is not True:
        n10 = _count_inn_checksum(inn[:9], coefs10)
        if n10 != int(inn[9]):
            raise INNValidationControlSumError
        return inn
    elif len(inn) == 12 and is_ip is not False:
        n11 = _count_inn_checksum(inn[:10], coefs11)
        if n11 != int(inn[10]):
            raise INNValidationControlSumError

        n12 = _count_inn_checksum(inn[:11], coefs12)
        if n12 != int(inn[11]):
            raise INNValidationControlSumError
        return inn
    elif len(inn) == 5:
        return inn

    raise INNValidationLenError


def validate_inn_ip(inn: str) -> Optional[str]:
    return validate_inn(inn, is_ip=True)


def validate_inn_le(inn: str) -> Optional[str]:
    return validate_inn(inn, is_ip=False)


def validate_kpp(kpp: str) -> Optional[str]:
    """
    Source: https://kontur.ru/bk/spravka/491-chtotakoe_kpp
    """
    if not isinstance(kpp, str):
        raise KPPValidationTypeError
    elif kpp in {'0', ''}:
        return None

    if len(kpp) != 9:
        raise KPPValidationValueLenError

    if not re.fullmatch(r'[0-9]{4}[0-9A-Z]{2}[0-9]{3}', kpp):
        raise KPPValidationValueError
    return kpp


def validate_bic(bic: str) -> str:
    """
    Source:
    https://ru.wikipedia.org/wiki/%D0%91%D0%B0%D0%BD%D0%BA%D0%BE%D0%B2%D1%81%D0%BA%D0%B8%D0%B9_%D0%B8%D0%B4%D0%B5%D0%BD%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%86%D0%B8%D0%BE%D0%BD%D0%BD%D1%8B%D0%B9_%D0%BA%D0%BE%D0%B4
    https://bik-info.ru/
    """
    if not isinstance(bic, str):
        raise BICValidationTypeError

    if len(bic) != 9:
        raise BICValidationLenError

    if not re.fullmatch(r'[0-9]+', bic):
        raise BICValidationValueDigitsOnlyError
    return bic


def validate_ogrn(ogrn: str, is_ip: Optional[bool] = None) -> None:
    """
    Source:
    https://ru.wikipedia.org/wiki/%D0%9E%D1%81%D0%BD%D0%BE%D0%B2%D0%BD%D0%BE%D0%B9_%D0%B3%D0%BE%D1%81%D1%83%D0%B4%D0%B0%D1%80%D1%81%D1%82%D0%B2%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9_%D1%80%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D0%BE%D0%BD%D0%BD%D1%8B%D0%B9_%D0%BD%D0%BE%D0%BC%D0%B5%D1%80
    """
    if not isinstance(ogrn, str):
        raise ValidationError('ogrn should be passed as string')

    if len(ogrn) != 13 and len(ogrn) != 15:
        raise ValidationError('wrong size of ogrn, it can be 13 chars only')

    if not re.fullmatch(r'[1-9][0-9]+', ogrn):
        raise ValidationError('wrong ogrn')

    if len(ogrn) == 13 and is_ip is not True:
        n13 = int(ogrn[:-1]) % 11 % 10
        if n13 != int(ogrn[12]):
            raise ValidationError(f'wrong checksum on pre-last digit: {ogrn[12]}; expected: {n13}')
        return

    if len(ogrn) == 15 and is_ip is not False:
        n15 = int(ogrn[:-1]) % 13 % 10
        if n15 != int(ogrn[14]):
            raise ValidationError(f'wrong checksum on pre-last digit: {ogrn[14]}; expected: {n15}')
        return

    raise ValidationError('ogrn for ip can be 15 chars only')


def validate_ogrnip(ogrnip: str) -> None:
    return validate_ogrn(ogrnip, is_ip=True)


def validate_snils(snils: str) -> None:
    """
    Source:
    https://www.consultant.ru/document/cons_doc_LAW_124607/68ac3b2d1745f9cc7d4332b63c2818ca5d5d20d0/
    """
    if not isinstance(snils, str):
        raise ValidationError('snils should be passed as string')

    if not re.fullmatch(r'[0-9]{11}', snils):
        raise ValidationError('wrong snils')

    if int(snils[:9]) < 1001998:  # less than 001-001-998
        raise ValidationError('snils must be more than "001-001-998" ')

    numbers = []
    parts = [snils[0:3], snils[3:6], snils[6:9]]
    for part in parts:
        numbers.extend([int(num) for num in part])

    results = [numbers[i - 1] * (10 - i) for i in range(1, 10)]
    checksum = sum(results)

    checksum = checksum % 101
    if checksum == 100:
        checksum_str = '00'
    elif checksum < 10:
        checksum_str = f'0{checksum}'
    else:
        checksum_str = str(checksum)

    if checksum_str != snils[-2:]:
        raise ValidationError(f'wrong checksum: {snils[-2:]}; expected: {checksum_str}')


def validate_oktmo(oktmo: str) -> Optional[str]:
    """
    Source:
    https://www.consultant.ru/cons/CGI/online.cgi?req=doc;base=LAW;n=149911#fUpVRbSdflobnNc4
    """
    if not isinstance(oktmo, str):
        raise OKTMOValidationTypeError
    elif oktmo in {'', '0'}:
        return None
    elif len(oktmo) not in {8, 11}:
        raise OKTMOValidationValueLenError
    if not re.fullmatch(r'([0-9]{11}|[0-9]{8})', oktmo):
        raise OKTMOValidationValueError
    return oktmo
