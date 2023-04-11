from typing import Any

from pydantic.errors import PydanticTypeError, PydanticValueError

from vitya.errors import (
    INNValidationError,
    INNValidationLenError,
    KPPValidationError,
    OktmoValidationError,
)
from vitya.payment_order.payments.helpers import (
    CHARS_FOR_PURPOSE,
    DOCUMENT_NUMBERS,
    PAYER_STATUSES,
    REASONS,
)


class PaymentTypeValueError(PydanticValueError):
    msg_template = 'invalid payment type: unknown payment type = '

    def __init__(self, payment_type: str, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
        super().__init__(*args, **kwargs)
        self.msg_template += payment_type


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


class OperationKindValidationTypeError(OperationKindValidationError, PydanticTypeError):
    msg_template = 'invalid operation kind: operation kind must be str'


class OperationKindValidationBudgetValueError(OperationKindValidationError):
    msg_template = 'invalid operation kind: for budget must be one of {"01", "02", "06"}'


class OperationKindValidationValueError(OperationKindValidationBudgetValueError):
    msg_template = 'invalid operation kind: value must be str with len 2'


class PurposeCodeValidationError(PydanticValueError):
    msg_template = 'invalid purpose code: base error'


class PurposeCodeValidationTypeError(PurposeCodeValidationError, PydanticTypeError):
    msg_template = 'invalid purpose: must be int'


class PurposeCodeValidationNullError(PurposeCodeValidationError):
    msg_template = 'invalid purpose code: for non fl payment value must be null'


class PurposeCodeValidationFlError(PurposeCodeValidationError):
    msg_template = 'invalid purpose code: for fl payment value must be in {1, 2, 3, 4, 5}'


class UINValidationError(PydanticValueError):
    msg_template = 'invalid uin: base error'


class UINValidationTypeError(UINValidationError, PydanticTypeError):
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


class PurposeValidationTypeError(PurposeValidationError, PydanticTypeError):
    msg_template = 'invalid purpose: must be str'


class PurposeValidationMaxLenError(PydanticValueError):
    msg_template = 'invalid purpose: purpose can be from 1 to 210 chars'


class PurposeValidationCharactersError(PurposeValidationError):
    msg_template = f'invalid purpose: the purpose can only consist of {CHARS_FOR_PURPOSE}'


class PurposeValidationIPNDSError(PurposeValidationError):
    msg_template = 'invalid purpose: for IP payment purpose must contains "НДС"'


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


class AccountNumberValidationTypeError(AccountNumberValidationError, PydanticTypeError):
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


class PayerStatusValidationTypeError(PayerStatusValidationError, PydanticTypeError):
    msg_template = 'invalid payer status: payer status must be str'


class PayerStatusValidationValueError(PayerStatusValidationError):
    msg_template = f'invalid payer status: value can be only {PAYER_STATUSES}'


class PayerStatusValidationNullNotAllowedError(PayerStatusValidationError):
    msg_template = 'invalid payer status: for budget payments empty value is not allowed'


class PayerStatusValidationCustoms05NotAllowedError(PayerStatusValidationError):
    msg_template = 'invalid payer status: for customs payment and for_third_face = true value "06" not allowed'


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


class PayeeKPPValidationStartsWithZeros(PayeeKPPValidationError):
    msg_template = 'invalid payee kpp: for fns, customs, budget other or le kpp cannot starts with "00"'


class CbcValidationError(PydanticValueError):
    msg_template = 'invalid cbc: base error'


class CbcValidationTypeError(CbcValidationError, PydanticTypeError):
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


class ReasonValidationError(PydanticValueError):
    msg_template = 'invalid reason: base error'


class ReasonValidationTypeError(ReasonValidationError, PydanticTypeError):
    msg_template = 'invalid reason: must be str'


class ReasonValidationFNSOnlyEmptyError(ReasonValidationError):
    msg_template = 'invalid reason: for fns only empty allowed'


class ReasonValidationValueLenError(ReasonValidationError):
    msg_template = 'invalid reason: reason must be 2 chars'


class ReasonValidationValueError(ReasonValidationError):
    msg_template = f'invalid reason: value must be in {REASONS}'


class TaxPeriodValidationError(PydanticValueError):
    msg_template = 'invalid tax period: base error'


class TaxPeriodValidationTypeError(TaxPeriodValidationError, PydanticTypeError):
    msg_template = 'invalid tax period: must be str'


class TaxPeriodValidationEmptyNotAllowed(TaxPeriodValidationError):
    msg_template = 'invalid tax period: empty is not allowed'


class TaxPeriodValidationValueLenError(TaxPeriodValidationError):
    msg_template = 'invalid tax period: invalid len'


class TaxPeriodValidationBOValueLenError(TaxPeriodValidationValueLenError):
    msg_template = 'invalid tax period: for bo must be 10'


class TaxPeriodValidationCustomsEmptyNotAllowed(TaxPeriodValidationEmptyNotAllowed):
    msg_template = 'invalid tax period: for customs empty is not allowed'


class TaxPeriodValidationCustomsValueLenError(TaxPeriodValidationValueLenError):
    msg_template = 'invalid tax period: for customs must be 8'


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


class DocumentNumberValidationTypeError(DocumentNumberValidationError, PydanticTypeError):
    msg_template = 'invalid document number: must be str'


class DocumentNumberValidationOnlyEmptyError(DocumentNumberValidationError):
    msg_template = 'invalid document number: only empty allowed'


class DocumentNumberValidationEmptyNotAllowed(DocumentNumberValidationError):
    msg_template = 'invalid document number: empty is not allowed'


class DocumentNumberValidationFNSOnlyEmptyError(DocumentNumberValidationOnlyEmptyError):
    msg_template = 'invalid document number: for fns only empty allowed'


class DocumentNumberValidationBOEmptyNotAllowed(DocumentNumberValidationEmptyNotAllowed):
    msg_template = (
        'invalid document number: for bo with payer status = "24", empty payer inn and empty uin empty is not allowed'
    )


class DocumentNumberValidationBOOnlyEmptyError(DocumentNumberValidationOnlyEmptyError):
    msg_template = (
        'invalid document number: for bo with payee account starts with "03212", '
        'payer status = "31", uin is not empty - empty value is not allowed'
    )


class DocumentNumberValidationBOValueError(DocumentNumberValidationError):
    msg_template = (
        f'invalid document number: for bo first two chars should be in {DOCUMENT_NUMBERS}, and third is equal to ";"'
    )


class DocumentNumberValidationBOValueLenError(DocumentNumberValidationError):
    msg_template = 'invalid document number: for bo value len max 15'


class DocumentNumberValidationCustoms00ValueError(DocumentNumberValidationError):
    msg_template = 'invalid document number: for customs with reason = "00" value must starts with "00"'


class DocumentNumberValidationCustomsValueLen7Error(DocumentNumberValidationError):
    msg_template = (
        'invalid document number: for customs with '
        'reason in {"ПК", "УВ", "ТГ", "ТБ", "ТД", "ПВ"} value len max 7'
    )


class DocumentNumberValidationCustomsValueLen15Error(DocumentNumberValidationError):
    msg_template = (
        'invalid document number: for customs with reason in {"ИЛ", "ИН", "ПБ", "КЭ"} '
        'value len from 1 to 15 chars'
    )


class DocumentDateValidationError(PydanticValueError):
    msg_template = 'invalid document date: base error'


class DocumentDateValidationTypeError(PydanticValueError, PydanticTypeError):
    msg_template = 'invalid document date: must be str'


class DocumentDateValidationFNSOnlyEmptyError(DocumentDateValidationError):
    msg_template = 'invalid document date: for fns only empty allowed'


class DocumentDateValidationCustomsLenError(DocumentDateValidationError):
    msg_template = 'invalid document date: for customs value must be equal 10 chars'


class DocumentDateValidationBOLenError(DocumentDateValidationError):
    msg_template = 'invalid document date: for customs value max 10 chars'
