from pydantic.errors import PydanticTypeError, PydanticValueError

from vitya.errors_base import VityaDescribedError


class OKTMOValidationError(VityaDescribedError, PydanticValueError):
    target = 'oktmo'
    target_ru = 'октмо'
    description = 'base error'
    description_ru = 'базовая ошибка'


class OKTMOValidationTypeError(OKTMOValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должен быть строкой'


class OKTMOValidationValueLenError(PydanticValueError):
    description = 'must be match 8 or 11 digits'
    description_ru = 'должен состоять из 8 или 11 цифр'


class OKTMOValidationValueError(PydanticValueError):
    description = 'must be match as ([0-9]{11}|[0-9]{8})'
    description_ru = 'должен матчиться с ([0-9]{11}|[0-9]{8})'


class INNValidationError(VityaDescribedError, PydanticValueError):
    target = 'inn'
    target_ru = 'инн'
    description = 'base error'
    description_ru = 'базовая ошибка'


class INNValidationControlSumError(INNValidationError):
    description = 'invalid control sum'
    description_ru = 'неверная контрольная сумма'


class INNValidationDigitsOnlyError(INNValidationError):
    description = 'must contains only digits'
    description_ru = 'может содержать только цифры'


class INNValidationLenError(INNValidationError):
    description = 'len must be 5, 10 or 12'
    description_ru = 'длина должна быть 5, 10 или 12 символов'


class INNValidationTypeError(INNValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должен быть строкой'


class INNValidationStartsWithZerosError(INNValidationError):
    description = 'cannot starts with "00"'
    description_ru = 'не может начинаться с "00"'


class KPPValidationError(VityaDescribedError, PydanticValueError):
    target = 'kpp'
    target_ru = 'кпп'
    description = 'base error'
    description_ru = 'базовая ошибка'


class KPPValidationTypeError(KPPValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должно быть строкой'


class KPPValidationValueLenError(KPPValidationError):
    description = 'kpp must be 9 chars'
    description_ru = 'должен содержать 9 символов'


class KPPValidationValueDigitsOnlyError(KPPValidationError):
    description = 'only digits allowed'
    description_ru = 'должен состоять только из цифр'


class KPPValidationValueError(KPPValidationError):
    description = 'must matches as [0-9]{4}[0-9A-Z]{2}[0-9]{3}'
    description_ru = 'должен матчиться с [0-9]{4}[0-9A-Z]{2}[0-9]{3}'


class KPPValidationValueCannotZerosStarts(KPPValidationError):
    description = 'cannot starts with "00"'
    description_ru = 'не может начинаться с "00"'


class BICValidationError(VityaDescribedError, PydanticValueError):
    target = 'bic'
    target_ru = 'бик'
    description = 'base error'
    description_ru = 'базовая ошибка'


class BICValidationTypeError(BICValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должен быть строкой'


class BICValidationLenError(BICValidationError):
    description = 'must be 9 chars'
    description_ru = 'должен содержать 9 символов'


class BICValidationValueDigitsOnlyError(BICValidationError):
    description = 'only digits allowed'
    description_ru = 'должен состоять только из чисел'
