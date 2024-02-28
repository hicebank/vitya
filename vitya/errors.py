from pydantic.errors import PydanticTypeError, PydanticValueError

from vitya.errors_base import (
    ExactFieldLenError,
    IncorrectData,
    IncorrectLen,
    VityaDescribedError,
)


class OKTMOValidationError(VityaDescribedError, PydanticValueError):
    target = 'oktmo'
    target_ru = 'ОКТМО'
    description = 'base error'
    description_ru = 'базовая ошибка'


class OKTMOValidationTypeError(OKTMOValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должен быть строкой'


class OKTMOValidationValueLenError(OKTMOValidationError, IncorrectLen):
    description = 'must be match 8 or 11 digits'
    description_ru = 'должен состоять из 8 или 11 цифр'


class OKTMOValidationValueError(OKTMOValidationError, IncorrectData):
    description = 'must be match as ([0-9]{11}|[0-9]{8})'
    description_ru = 'должен матчиться с ([0-9]{11}|[0-9]{8})'


class INNValidationError(VityaDescribedError, PydanticValueError):
    target = 'inn'
    target_ru = 'ИНН'
    description = 'base error'
    description_ru = 'базовая ошибка'


class INNValidationControlSumError(INNValidationError, IncorrectData):
    description = 'invalid control sum'
    description_ru = 'неверная контрольная сумма'


class INNValidationDigitsOnlyError(INNValidationError, IncorrectData):
    description = 'must contains only digits'
    description_ru = 'может содержать только цифры'


class INNValidationLenError(INNValidationError, IncorrectLen):
    description = 'len must be 5, 10 or 12'
    description_ru = 'длина должна быть 5, 10 или 12 символов'


class INNValidationTypeError(INNValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должен быть строкой'


class INNValidationStartsWithZerosError(INNValidationError, IncorrectData):
    description = 'cannot starts with "00"'
    description_ru = 'не может начинаться с "00"'


class KPPValidationError(VityaDescribedError, PydanticValueError):
    target = 'kpp'
    target_ru = 'КПП'
    description = 'base error'
    description_ru = 'базовая ошибка'


class KPPValidationTypeError(KPPValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должно быть строкой'


class KPPValidationValueLenError(KPPValidationError, ExactFieldLenError):
    description = 'kpp must be 9 chars'
    description_ru = 'должен содержать 9 символов'
    required_len = 9


class ReceiverKPPValidationValueDigitsOnlyError(KPPValidationError, IncorrectData):
    description = 'only digits allowed'
    description_ru = 'должен состоять только из цифр'
    target = 'receiver kpp'


class PayerKPPValidationValueDigitsOnlyError(KPPValidationError, IncorrectData):
    description = 'only digits allowed'
    description_ru = 'должен состоять только из цифр'
    target = 'payer kpp'


class KPPValidationValueError(KPPValidationError, IncorrectData):
    description = 'must matches as [0-9]{4}[0-9A-Z]{2}[0-9]{3}'
    description_ru = 'должен матчиться с [0-9]{4}[0-9A-Z]{2}[0-9]{3}'


class PayerKPPValidationValueCannotZerosStarts(KPPValidationError, IncorrectData):
    description = 'cannot starts with "00"'
    description_ru = 'не может начинаться с "00"'
    target = 'payer kpp'


class ReceiverKPPValidationValueCannotZerosStarts(KPPValidationError, IncorrectData):
    description = 'cannot starts with "00"'
    description_ru = 'не может начинаться с "00"'
    target = 'receiver kpp'


class BICValidationError(VityaDescribedError, PydanticValueError):
    target = 'bic'
    target_ru = 'БИК'
    description = 'base error'
    description_ru = 'базовая ошибка'


class BICValidationTypeError(BICValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должен быть строкой'


class BICValidationLenError(BICValidationError, ExactFieldLenError):
    description = 'must be 9 chars'
    description_ru = 'должен содержать 9 символов'
    required_len = 9


class BICValidationValueDigitsOnlyError(BICValidationError):
    description = 'only digits allowed'
    description_ru = 'должен состоять только из чисел'
