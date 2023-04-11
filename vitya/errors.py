from pydantic.errors import PydanticTypeError, PydanticValueError


class OktmoValidationError(PydanticValueError):
    msg_template = 'invalid oktmo: base error'


class OktmoValidationTypeError(OktmoValidationError, PydanticTypeError):
    msg_template = 'invalid oktmo: must be str'


class OktmoValidationValueLenError(PydanticValueError):
    msg_template = 'invalid oktmo: must be match 8 or 11 digits'


class OktmoValidationValueError(PydanticValueError):
    msg_template = 'invalid oktmo: must be match as ([0-9]{11}|[0-9]{8})'


class INNValidationError(PydanticValueError):
    msg_template = 'invalid inn: base error'


class INNValidationControlSumError(INNValidationError):
    msg_template = 'invalid inn: invalid control sum'


class INNValidationDigitsOnlyError(INNValidationError):
    msg_template = 'invalid inn: inn must contains only digits'


class INNValidationLenError(INNValidationError):
    msg_template = 'invalid inn: len inn must be 5, 10 or 12'


class INNValidationTypeError(INNValidationError, PydanticTypeError):
    msg_template = 'invalid inn: must be str'


class INNValidationStartsWithZerosError(INNValidationError):
    msg_template = 'invalid inn: cannot starts with "00"'


class KPPValidationError(PydanticValueError):
    msg_template = 'invalid kpp: base error'


class KPPValidationTypeError(KPPValidationError, PydanticTypeError):
    msg_template = 'invalid kpp: must be str'


class KPPValidationValueLenError(KPPValidationError):
    msg_template = 'invalid kpp: kpp must be 9 chars'


class KPPValidationValueDigitsOnlyError(KPPValidationError):
    msg_template = 'invalid kpp: only digits allowed'


class KPPValidationValueError(KPPValidationError):
    msg_template = 'invalid kpp: must matches as [0-9]{4}[0-9A-Z]{2}[0-9]{3}'


class KPPValidationValueCannotZerosStarts(KPPValidationError):
    msg_template = 'invalid kpp: cannot starts with "00"'


class BICValidationError(PydanticValueError):
    msg_template = 'invalid bic: base error'


class BICValidationTypeError(BICValidationError, PydanticTypeError):
    msg_template = 'invalid bic: must be str'


class BICValidationLenError(BICValidationError):
    msg_template = 'invalid bic: must be 9 chars'


class BICValidationValueDigitsOnlyError(BICValidationError):
    msg_template = 'invalid bic: only digits allowed'
