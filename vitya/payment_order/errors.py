from pydantic.errors import PydanticValueError

from vitya.payment_order.payments.helpers import CHARS_FOR_PURPOSE, PAYER_STATUSES
from vitya.validators import OktmoValidationError


class AmountValidationError(PydanticValueError):
    msg_template = 'invalid amount: base error'


class AmountValidationLengthError(AmountValidationError):
    msg_template = 'invalid amount: amount as str cannot contains more 18 chars'


class AmountValidationLessOrEqualZeroError(AmountValidationError):
    msg_template = 'invalid amount: amount cannot be less than or equal to 0.0'


class CustomerValidationError(PydanticValueError):
    msg_template = 'invalid customer: base error'


class CustomerValidationSizeError(CustomerValidationError):
    msg_template = 'invalid customer: customer name must sized from 1 to 160 chars'


class PayerValidationError(CustomerValidationError):
    msg_template = 'invalid payer: base error'


class PayerValidationSizeError(PayerValidationError, CustomerValidationSizeError):
    msg_template = 'invalid payer: payer name must sized from 1 to 160 chars'


class PayeeValidationError(CustomerValidationError):
    msg_template = 'invalid payee: base error'


class PayeeValidationSizeError(PayeeValidationError, CustomerValidationSizeError):
    msg_template = 'invalid payee: payee name must sized from 1 to 160 chars'


class PayeeValidationNameError(CustomerValidationError):
    msg_template = 'invalid payee: account in name'


class NumberValidationLenError(PydanticValueError):
    msg_template = 'invalid number: number cannot be more 6'


class PaymentOrderValidationError(PayerValidationError):
    msg_template = 'invalid payment order: value must be in {1, 2, 3, 4, 5}'


class OperationKindValidationError(PydanticValueError):
    msg_template = 'invalid operation kind: base error'


class OperationKindValidationTypeError(OperationKindValidationError):
    msg_template = 'invalid operation kind: operation kind must be str'


class OperationKindValidationBudgetValueError(OperationKindValidationError):
    msg_template = 'invalid operation kind: for budget must be one of {"01", "02", "06"}'


class OperationKindValidationValueError(OperationKindValidationBudgetValueError):
    msg_template = 'invalid operation kind: value must be str with len 2'


class PurposeCodeValidationError(PydanticValueError):
    msg_template = 'invalid purpose code: base error'


class PurposeCodeValidationTypeError(PurposeCodeValidationError):
    msg_template = 'invalid purpose: must be int'


class PurposeCodeValidationNullError(PurposeCodeValidationError):
    msg_template = 'invalid purpose code: for non fl payment value must be null'


class PurposeCodeValidationFlError(PurposeCodeValidationError):
    msg_template = 'invalid purpose code: for fl payment value must be in {1, 2, 3, 4, 5}'


class UINValidationError(PydanticValueError):
    msg_template = 'invalid uin: base error'


class UINValidationTypeError(UINValidationError):
    msg_template = 'invalid uin: must be str'


class UINValidationLenError(UINValidationError):
    msg_template = 'invalid uin: len uin must be 4, 20 or 25 len'


class UINValidationDigitsOnlyError(UINValidationError):
    msg_template = 'invalid uin: uin must contains only digits'


class UINValidationControlSumError(UINValidationError):
    msg_template = 'invalid uin: control sum error'


class UINValidationValueZeroError(UINValidationError):
    msg_template = 'invalid uin: value cannot be zero'


class UINValidationBOLenError(UINValidationLenError):
    msg_template = 'invalid uin: len uin for bo payment must be 4, 20 or 25 len'


class UINValidationBOValueError(UINValidationError):
    msg_template = (
        'invalid uin: for bo payment with payee account start with '
        "('03212', '03222', '03232', '03242', '03252', '03262', '03272') uin must be non zero"
    )


class UINValidationFNSValueError(UINValidationError):
    msg_template = 'invalid uin: FNS base error'


class UINValidationFNSValueZeroError(UINValidationFNSValueError):
    msg_template = (
        'invalid uin: for FNS with payer status = "13" and empty inn uin must be non zero'
    )


class UINValidationFNSNotValueZeroError(UINValidationFNSValueError):
    msg_template = 'invalid uin: for FNS with payer status = "02" uin must be zero'


class UINValidationFNSLenError(UINValidationLenError):
    msg_template = 'invalid uin: len uin for FNS payment must be 20 or 25 len'


class UINValidationOnlyZeroError(UINValidationError):
    msg_template = 'invalid uin: uin cannot contains only 0 chars'


class PurposeValidationError(PydanticValueError):
    msg_template = 'invalid purpose: base error'


class PurposeValidationTypeError(PurposeValidationError):
    msg_template = 'invalid purpose: must be str'


class PurposeValidationMaxLenError(PydanticValueError):
    msg_template = 'invalid purpose: purpose can be from 1 to 210 chars'


class PurposeValidationCharactersError(PurposeValidationError):
    msg_template = f'invalid purpose: the purpose can only consist of {CHARS_FOR_PURPOSE}'


class PurposeValidationIPNDSError(PurposeValidationError):
    msg_template = 'invalid purpose: for IP payment purpose must contains "НДС"'


class INNValidationError(PydanticValueError):
    msg_template = 'invalid inn: base error'


class INNValidationControlSumError(INNValidationError):
    msg_template = 'invalid inn: invalid control sum'


class INNValidationDigitsOnlyError(INNValidationError):
    msg_template = 'invalid inn: inn must contains only digits'


class INNValidationLenError(INNValidationError):
    msg_template = 'invalid inn: len inn must be 5, 10 or 12'


class PayerINNValidationCustomsLenError(INNValidationLenError):
    msg_template = 'invalid inn: customs len inn base error'


class PayerINNValidationCustomsLen10Error(INNValidationLenError):
    msg_template = 'invalid inn: for customs payment and payer status 06, inn must be 10'


class PayerINNValidationCustomsLen12Error(INNValidationLenError):
    msg_template = 'invalid inn: for customs payment and payer status 16 or 17, inn must be 12'


class PayerINNValidationEmptyNotAllowedError(INNValidationError):
    msg_template = 'invalid inn: inn cannot be empty'


class PayerINNValidationStartWithZerosError(INNValidationError):
    msg_template = 'invalid inn: inn cannot start with "00"'


class PayerINNValidationFiveOnlyZerosError(INNValidationError):
    msg_template = 'invalid inn: inn with len 5 cannot be contains only zeros'


class PayeeINNValidationNonEmptyError(INNValidationError):
    msg_template = 'invalid payee inn: payee inn cannot be empty'


class PayeeINNValidationFLenError(INNValidationLenError):
    msg_template = 'invalid payee inn: for fl payee inn must be 12'


class PayeeINNValidationFLLenError(INNValidationLenError):
    msg_template = 'invalid payee inn: for fl payee inn must be empty or 12 chars'


class PayeeINNValidationIPLenError(INNValidationError):
    msg_template = 'invalid payee inn: for ip payee inn must be 12'


class PayeeINNValidationLELenError(INNValidationError):
    msg_template = 'invalid inn: for fns, customs, bo and le inn must be 10'


class PayerAccountValidationError(PydanticValueError):
    msg_template = 'invalid payer account: base error'


class PayeeAccountValidationError(PydanticValueError):
    msg_template = 'invalid payee account: base error'


class PayeeAccountValidationNonEmptyError(PayeeAccountValidationError):
    msg_template = 'invalid payee account: account cannot be empty'


class PayeeAccountValidationLenError(PayeeAccountValidationError):
    msg_template = 'invalid payee account: account must be 20 digits'


class PayeeAccountValidationFNSValueError(PayeeAccountValidationError):
    msg_template = 'invalid payee account: for FNS payment account must be "03100643000000018500"'


class AccountNumberValidationError(PydanticValueError):
    msg_template = 'invalid account number: base error'


class AccountNumberValidationTypeError(AccountNumberValidationError):
    msg_template = 'invalid account number: account number must be str'


class AccountNumberValidationSizeError(AccountNumberValidationError):
    msg_template = 'invalid account number: account number must be 20 chars'


class AccountNumberValidationDigitsOnlyError(AccountNumberValidationError):
    msg_template = 'invalid account number: account number must be only digits'


class AccountValidationBICValueError(AccountNumberValidationError):
    msg_template = 'invalid account: account is not valid for bic'


class PayerAccountValidationBICValueError(PayerAccountValidationError, AccountValidationBICValueError):
    msg_template = 'invalid payer account: value is invalid for received bic'


class PayeeAccountValidationBICValueError(PayeeAccountValidationError, AccountValidationBICValueError):
    msg_template = 'invalid payee account: value is invalid for received bic'


class PayerStatusValidationError(PydanticValueError):
    msg_template = 'invalid payer status: base error'


class PayerStatusValidationTypeError(PayerStatusValidationError):
    msg_template = 'invalid payer status: payer status must be str'


class PayerStatusValidationValueError(PayerStatusValidationError):
    msg_template = f'invalid payer status: value can be only {PAYER_STATUSES}'


class PayerStatusValidationNullNotAllowedError(PayerStatusValidationError):
    msg_template = 'invalid payer status: for budget payments empty value is not allowed'


class PayerStatusValidationCustoms05NotAllowedError(PayerStatusValidationError):
    msg_template = 'invalid payer status: for customs payment and for_third_face = true value "06" not allowed'


class KPPValidationError(PydanticValueError):
    msg_template = 'invalid kpp: base error'


class KPPValidationValueLenError(KPPValidationError):
    msg_template = 'invalid kpp: kpp must be 9'


class KPPValidationValueDigitsOnlyError(KPPValidationError):
    msg_template = 'invalid kpp: only digits allowed'


class KPPValidationValueCannotZerosStarts(KPPValidationError):
    msg_template = 'invalid kpp: cannot starts with "00"'


class KPPValidationOnlyEmptyError(KPPValidationError):
    msg_template = 'invalid kpp: only empty allowed'


class KPPValidationEmptyNotAllowed(KPPValidationError):
    msg_template = 'invalid kpp: empty value is not allowed'


class PayerKPPValidationError(KPPValidationError):
    msg_template = 'invalid payer kpp: base error'


class PayerKPPValidationOnlyEmptyError(PayerKPPValidationError, KPPValidationOnlyEmptyError):
    msg_template = 'invalid payer kpp: for ip, fl or le allowed empty value'


class PayerKPPValidationINN10EmptyNotAllowed(PayerKPPValidationError, KPPValidationEmptyNotAllowed):
    msg_template = 'invalid payer kpp: for tns, tms or bo with inn = 10 inn empty value is not allowed'


class PayerKPPValidationINN12OnlyEmptyError(PayerKPPValidationOnlyEmptyError):
    msg_template = 'invalid payer kpp: for fns, tms or bo with inn = 12 only empty allowed'


class PayeeKPPValidationError(KPPValidationError):
    msg_template = 'invalid payee kpp: base error'


class PayeeKPPValidationOnlyEmptyError(PayeeKPPValidationError, KPPValidationOnlyEmptyError):
    msg_template = 'invalid payee kpp: for ip or fl only empty allowed'


class PayeeKPPValidationEmptyNotAllowed(PayeeKPPValidationError, KPPValidationEmptyNotAllowed):
    msg_template = 'invalid payee kpp: for fns, customs, budget other or le empty value is not allowed'


class CbcValidationError(PydanticValueError):
    msg_template = 'invalid cbc: base error'


class CbcValidationTypeError(CbcValidationError):
    msg_template = 'invalid cbc: cbc must be str'


class CbcValidationEmptyNotAllowed(CbcValidationError):
    msg_template = 'invalid cbc: for fns or tms empty value is not allowed'


class CbcValidationValueLenError(CbcValidationError):
    msg_template = 'invalid cbc: cbc must be 20 digits'


class CbcValidationValueDigitsOnlyError(CbcValidationError):
    msg_template = 'invalid cbc: only digits allowed'


class CbcValidationValueCannotZerosOnly(CbcValidationError):
    msg_template = 'invalid cbc: cannot contain only zeros'


class OktmoValidationEmptyNotAllowed(OktmoValidationError):
    msg_template = 'invalid oktmo: empty value is not allowed'


class OktmoValidationFNSEmptyNotAllowed(OktmoValidationEmptyNotAllowed):
    msg_template = 'invalid oktmo: for fns with payer status = "02" empty value is not allowed'


class OktmoValidationZerosNotAllowed(OktmoValidationError):
    msg_template = 'invalid oktmo: cannot be all zeros'
