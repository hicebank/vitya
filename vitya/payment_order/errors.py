from typing import Any

from pydantic.errors import PydanticValueError

from vitya.payment_order.enums import PaymentType
from vitya.payment_order.payments.helpers import (
    CHARS_FOR_PURPOSE,
    DOCUMENT_NUMBERS,
    PAYER_STATUSES,
    REASONS,
)


class PaymentTypeValueError(PydanticValueError):
    msg_template = 'invalid payment type: unknown payment type = '

    def __init__(self, _type: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.msg_template += _type


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


class PayeeINNValidationFLLenError(INNValidationLenError):
    msg_template = 'invalid inn: for fl payee inn must be 0 or 12'


class PayeeINNValidationIPLenError(INNValidationError):
    msg_template = 'invalid inn: for ip payee inn must be 12'


class PayeeINNValidationLELenError(INNValidationError):
    msg_template = 'invalid inn: for fns, tms, bo and le inn must be 10'


class PayeeINNValidationControlSumError(INNValidationError):
    msg_template = 'invalid inn: inn control sum error'


class PayeeAccountValidationError(PydanticValueError):
    msg_template = 'invalid payee account: base error'


class PayeeAccountValidationNonEmptyError(PayeeAccountValidationError):
    msg_template = 'invalid payee account: account cannot be empty'


class PayeeAccountValidationLenError(PayeeAccountValidationError):
    msg_template = 'invalid payee account: account must be 20 digits'


class PayeeAccountValidationFNSValueError(PayeeAccountValidationError):
    msg_template = 'invalid payee account: for fns payment account must be "03100643000000018500"'


class PayerStatusValidationError(PydanticValueError):
    msg_template = 'invalid payer status: base error'


class PayerStatusValidationNullNotAllowedError(PayerStatusValidationError):
    msg_template = 'invalid payer status: for budget payments empty value is not allowed'


class PayerStatusValidationTMS05NotAllowedError(PayerStatusValidationError):
    msg_template = 'invalid payer status: for tms payment and for_third_face = true value "06" not allowed'


class PayerStatusValidationValueError(PayerStatusValidationError):
    msg_template = f'invalid payer status: value can be only {PAYER_STATUSES}'


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


class PayerKPPValidationValueLenError(PayerKPPValidationError, KPPValidationValueLenError):
    msg_template = 'invalid payer kpp: kpp must be 9'


class PayerKPPValidationValueDigitsOnlyError(PayerKPPValidationError, KPPValidationValueDigitsOnlyError):
    msg_template = 'invalid payer kpp: only digits allowed'


class PayerKPPValidationValueCannotZerosStarts(PayerKPPValidationError, KPPValidationValueCannotZerosStarts):
    msg_template = 'invalid payer kpp: cannot starts with "00" '


class PayeeKPPValidationError(KPPValidationError):
    msg_template = 'invalid payee kpp: base error'


class PayeeKPPValidationOnlyEmptyError(PayeeKPPValidationError, KPPValidationOnlyEmptyError):
    msg_template = 'invalid payee kpp: for ip or fl only empty allowed'


class PayeeKPPValidationValueLenError(PayeeKPPValidationError, KPPValidationValueLenError):
    msg_template = 'invalid payer kpp: kpp must be 9'


class PayeeKPPValidationValueDigitsOnlyError(PayeeKPPValidationError, KPPValidationValueDigitsOnlyError):
    msg_template = 'invalid payer kpp: only digits allowed'


class PayeeKPPValidationEmptyNotAllowed(PayeeKPPValidationError, KPPValidationEmptyNotAllowed):
    msg_template = 'invalid payee kpp: for fns, tms, bo or le empty value is not allowed'


class PayeeKPPValidationValueCannotZerosStarts(PayeeKPPValidationError, KPPValidationValueCannotZerosStarts):
    msg_template = 'invalid payee kpp: cannot starts with "00"'


class CBCValidationError(PydanticValueError):
    msg_template = 'invalid cbc: base error'


class CBCValidationEmptyNotAllowed(CBCValidationError):
    msg_template = 'invalid cbc: for fns or tms empty value is not allowed'


class CBCValidationValueLenError(CBCValidationError):
    msg_template = 'invalid cbc: cbc must be 20'


class CBCValidationValueDigitsOnlyError(CBCValidationError):
    msg_template = 'invalid cbc: only digits allowed'


class CBCValidationValueCannotZerosStarts(CBCValidationError):
    msg_template = 'invalid cbc: cannot starts with "00"'


class OKTMOValidationError(PydanticValueError):
    msg_template = 'invalid oktmo: base error'


class OKTMOValidationEmptyNotAllowed(OKTMOValidationError):
    msg_template = 'invalid oktmo: empty value is not allowed'


class OKTMOValidationFNSEmptyNotAllowed(OKTMOValidationEmptyNotAllowed):
    msg_template = 'invalid oktmo: for fns with payer status = "02" empty value is not allowed'


class OKTMOValidationValueLenError(OKTMOValidationError):
    msg_template = 'invalid oktmo: oktmo must be 8 or 11'


class OKTMOValidationZerosNotAllowed(OKTMOValidationError):
    msg_template = 'invalid oktmo: cannot be all zeros'


class ReasonValidationError(PydanticValueError):
    msg_template = 'invalid reason: base error'


class ReasonValidationFNSOnlyEmptyError(ReasonValidationError):
    msg_template = 'invalid reason: for fns only empty allowed'


class ReasonValidationEmptyNotAllowed(ReasonValidationError):
    msg_template = 'invalid reason: empty value is not allowed'


class ReasonValidationValueLenError(ReasonValidationError):
    msg_template = 'invalid reason: reason must be 2'


class ReasonValidationValueError(ReasonValidationError):
    msg_template = f'invalid reason: value must be in {REASONS}'


class TaxPeriodValidationError(PydanticValueError):
    msg_template = 'invalid tax period: base error'


class TaxPeriodValidationValueLenError(TaxPeriodValidationError):
    msg_template = 'invalid tax period: invalid len'


class TaxPeriodValidationBOValueLenError(TaxPeriodValidationValueLenError):
    msg_template = 'invalid tax period: for bo must be 10'


class TaxPeriodValidationEmptyNotAllowed(TaxPeriodValidationError):
    msg_template = 'invalid tax period: empty is not allowed'


class TaxPeriodValidationTMSEmptyNotAllowed(TaxPeriodValidationEmptyNotAllowed):
    msg_template = 'invalid tax period: for tms empty is not allowed'


class TaxPeriodValidationTMSValueLenError(TaxPeriodValidationValueLenError):
    msg_template = 'invalid tax period: for tms must be 8'


class TaxPeriodValidationFNS02EmptyNotAllowed(TaxPeriodValidationError):
    msg_template = 'invalid tax period: for fns with payer status = "02" empty is not allowed'


class TaxPeriodValidationFNS01OnlyEmpty(TaxPeriodValidationError):
    msg_template = 'invalid tax period: for fns with payer status = "01" or "13" only empty allowed'


class TaxPeriodValidationFNSEmptyNotAllowed(TaxPeriodValidationEmptyNotAllowed):
    msg_template = 'invalid tax period: for fns empty is not allowed'


class TaxPeriodValidationFNSValueLenError(TaxPeriodValidationValueLenError):
    msg_template = 'invalid tax period: for fns must be 10'


class DocumentNumberValidationError(PydanticValueError):
    msg_template = 'invalid document number: base error'


class DocumentNumberValidationOnlyEmptyError(DocumentNumberValidationError):
    msg_template = 'invalid document number: only empty allowed'


class DocumentNumberValidationEmptyNotAllowed(DocumentNumberValidationError):
    msg_template = 'invalid document number: empty is not allowed'


class DocumentNumberValidationFNSOnlyEmptyError(DocumentNumberValidationOnlyEmptyError):
    msg_template = 'invalid document number: for fns only empty allowed'


class DocumentNumberValidationBOEmptyNotAllowed(DocumentNumberValidationEmptyNotAllowed):
    msg_template = 'invalid document number: for bo with payer status = "24", empty payer inn and empty uin ' \
                   'empty is not allowed'


class DocumentNumberValidationBOOnlyEmptyError(DocumentNumberValidationOnlyEmptyError):
    msg_template = 'invalid document number: for bo with payee account starts with "03212", ' \
                   'payer status = "31", uin is not empty - empty value is not allowed'


class DocumentNumberValidationBOValueLenError(DocumentNumberValidationError):
    msg_template = 'invalid document number: for bo value len max 15'


class DocumentNumberValidationBOValueError(DocumentNumberValidationError):
    msg_template = f'invalid document number: for bo first two chars should be in {DOCUMENT_NUMBERS}, ' \
                   f'and third is equal to ";"'


class DocumentNumberValidationTMS00ValueError(DocumentNumberValidationError):
    msg_template = 'invalid document number: for tms with reason = "00" value must starts with "00"'


class DocumentNumberValidationTMSValueLen7Error(DocumentNumberValidationError):
    msg_template = 'invalid document number: for tms with reason in {"ПК", "УВ", "ТГ", "ТБ", "ТД", "ПВ"} ' \
                   'value len max 7'


class DocumentNumberValidationTMSValueLen15Error(DocumentNumberValidationError):
    msg_template = 'invalid document number: for tms with reason in {"ИЛ", "ИН", "ПБ", "КЭ"} ' \
                   'value len from 1 to 15 chars'
