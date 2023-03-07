from pydantic.errors import PydanticValueError


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
