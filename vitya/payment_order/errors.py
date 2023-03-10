from pydantic.errors import PydanticValueError

from vitya.payment_order.payments.helpers import CHARS_FOR_PURPOSE


class AmountValidationError(PydanticValueError):
    msg_template = 'invalid amount: base error'


class AmountValidationLengthError(AmountValidationError):
    msg_template = 'invalid amount: amount as str cannot contains more 18 chars'


class AmountValidationEqualZeroError(AmountValidationError):
    msg_template = 'invalid amount: amount cannot be equal 0.0'


class CustomerValidationError(PydanticValueError):
    msg_template = 'invalid customer: base error'


class PayerValidationError(CustomerValidationError):
    msg_template = 'invalid payer: base error'


class PayerValidationSizeError(PayerValidationError):
    msg_template = 'invalid payer: payer name must sized from 1 to 160 chars'


class PayeeValidationNameError(CustomerValidationError):
    msg_template = 'invalid payee: account in name'


class NumberValidationLenError(PydanticValueError):
    msg_template = 'invalid number: number cannot be more 6'


class PaymentOrderValidationError(PayerValidationError):
    msg_template = 'invalid payment order: value must be in {1, 2, 3, 4, 5}'


class OperationKindValidationError(PydanticValueError):
    msg_template = 'invalid operation kind: base error'


class OperationKindValidationBudgetValueError(OperationKindValidationError):
    msg_template = 'invalid operation kind: for budget must be one of {"01", "02", "06"}'


class OperationKindValidationValueError(OperationKindValidationBudgetValueError):
    msg_template = 'invalid operation kind: value must be str with len 2'


class PurposeCodeValidationError(PydanticValueError):
    msg_template = 'invalid purpose code: base error'


class PurposeCodeValidationNullError(PurposeCodeValidationError):
    msg_template = 'invalid purpose code: for non fl payment value must be null'


class PurposeCodeValidationFlError(PurposeCodeValidationError):
    msg_template = 'invalid purpose code: for fl payment value must be in {1, 2, 3, 4, 5}'


class UINValidationError(PydanticValueError):
    msg_template = 'invalid uin: base error'


class UINValidationDigitsOnlyError(UINValidationError):
    msg_template = 'invalid uin: uin must contains only digits'


class UINValidationControlSumError(UINValidationError):
    msg_template = 'invalid uin: control sum error'


class UINValidationValueZeroError(UINValidationError):
    msg_template = 'invalid uin: value cannot be zero'


class UINValidationBOLenError(UINValidationError):
    msg_template = 'invalid uin: len uin for bo payment must be 4, 20 or 25 len'


class UINValidationBOValueError(UINValidationError):
    msg_template = 'invalid uin: for bo payment with payee account start with ' \
                   "('03212', '03222', '03232', '03242', '03252', '03262', '03272') uin must be non zero"


class UINValidationFNSValueError(UINValidationError):
    msg_template = 'invalid uin: fns base error'


class UINValidationFNSValueZeroError(UINValidationFNSValueError):
    msg_template = 'invalid uin: for fns with payer status = "13" and empty inn ' \
                   'uin must be non zero'


class UINValidationFNSNotValueZeroError(UINValidationFNSValueError):
    msg_template = 'invalid uin: for fns with payer status = "02" uin must be zero'


class UINValidationLenError(UINValidationError):
    msg_template = 'invalid uin: len uin for fns payment must be 20 or 25 len'


class UINValidationOnlyZeroError(UINValidationError):
    msg_template = 'invalid uin: uin cannot contains only 0 chars'


class PurposeValidationError(PydanticValueError):
    msg_template = 'invalid purpose: base error'


class PurposeValidationMaxLenError(PydanticValueError):
    msg_template = 'invalid purpose: purpose can be from 1 to 210 chars'


class PurposeValidationCharactersError(PurposeValidationError):
    msg_template = f'invalid purpose: the purpose can only consist of {CHARS_FOR_PURPOSE}'


class PurposeValidationIPNDSError(PurposeValidationError):
    msg_template = 'invalid purpose: for IP payment purpose must contains "НДС"'


class INNValidationError(PydanticValueError):
    msg_template = 'invalid inn: base error'


class INNValidationDigitsOnlyError(INNValidationError):
    msg_template = 'invalid inn: inn must contains only digits'


class INNValidationLenError(INNValidationError):
    msg_template = 'invalid inn: len inn must be 5, 10 or 12'


class PayerINNValidationTMSLenError(INNValidationLenError):
    msg_template = 'invalid inn: tms len inn base error'


class PayerINNValidationTMSLen10Error(INNValidationLenError):
    msg_template = 'invalid inn: for tms payment and payer status 06, inn must be 10'


class PayerINNValidationTMSLen12Error(INNValidationLenError):
    msg_template = 'invalid inn: for tms payment and payer status 16 or 17, inn must be 12'


class PayerINNValidationEmptyNotAllowedError(INNValidationError):
    msg_template = 'invalid inn: inn cannot be empty'


class PayerINNValidationStartWithZerosError(INNValidationError):
    msg_template = 'invalid inn: inn cannot start with "00"'


class PayerINNValidationFiveOnlyZerosError(INNValidationError):
    msg_template = 'invalid inn: inn with len 5 cannot be contains only zeros'


class PayeeINNValidationFLenError(INNValidationLenError):
    msg_template = 'invalid inn: for fl payee inn must be 12'


class PayeeAccountValidationError(PydanticValueError):
    msg_template = 'invalid payee account: base error'


class PayeeAccountValidationNonEmptyError(PayeeAccountValidationError):
    msg_template = 'invalid payee account: account cannot be empty'


class PayeeAccountValidationLenError(PayeeAccountValidationError):
    msg_template = 'invalid payee account: account must be 20 digits'


class PayeeAccountValidationFNSValueError(PayeeAccountValidationError):
    msg_template = 'invalid payee account: for fns payment account must be "03100643000000018500"'
