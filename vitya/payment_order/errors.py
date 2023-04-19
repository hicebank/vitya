from typing import Any

from pydantic.errors import PydanticTypeError, PydanticValueError

from vitya.errors import (
    INNValidationError,
    INNValidationLenError,
    KPPValidationError,
    OKTMOValidationError,
)
from vitya.errors_base import VityaDescribedError
from vitya.payment_order.enums import PaymentType
from vitya.payment_order.payments.constants import (
    CHARS_FOR_PURPOSE,
    CUSTOMS_REASONS,
    DOCUMENT_NUMBERS,
    PAYER_STATUSES,
)


class PaymentTypeValueError(VityaDescribedError, PydanticValueError):
    target = 'payment type'
    target_ru = 'тип платежа'
    description = 'неизвестный тип платежа '
    description_ru = 'неизвестный тип платежа '

    def __init__(self, payment_type: PaymentType, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
        super().__init__(*args, **kwargs)
        self.description += payment_type.name
        self.description_ru += payment_type.name_ru


class AmountValidationError(VityaDescribedError, PydanticValueError):
    target = 'amount'
    target_ru = 'сумма'
    description = 'base error'
    description_ru = 'базовая ошибка'


class AmountValidationLengthError(AmountValidationError):
    description = 'str representation cannot contains more 18 chars'
    description_ru = 'строковое представление не может содержать более 18 символов'


class AmountValidationLessOrEqualZeroError(AmountValidationError):
    description = 'cannot be less than or equal to 0.0'
    description_ru = 'не может быть меньше или равно 0.0'


class CustomerValidationError(VityaDescribedError, PydanticValueError):
    target = 'customer'
    target_ru = 'плательщик или получатель'
    description = 'base error'
    description_ru = 'базовая ошибка'


class CustomerValidationSizeError(CustomerValidationError):
    description = 'name must sized from 1 to 160 chars'
    description_ru = 'длина имени должно быть между 1 и 160 символами'


class PayerValidationError(CustomerValidationError):
    target = 'payer'
    target_ru = 'плательщик'


class PayerValidationSizeError(PayerValidationError, CustomerValidationSizeError):
    pass


class PayeeValidationError(CustomerValidationError):
    target = 'payee'
    target_ru = 'получатель'


class PayeeValidationSizeError(PayeeValidationError, CustomerValidationSizeError):
    pass


class PayeeValidationNameError(PayeeValidationError):
    description = 'contains account number'
    description_ru = 'содержит номер счета'


class NumberValidationLenError(VityaDescribedError, PydanticValueError):
    target = 'number'
    target_ru = 'номер'
    description = 'cannot be longer than 6 chars'
    description_ru = 'не может быть длиннее 6 символов'


class PaymentOrderValidationError(VityaDescribedError, PydanticValueError):
    target = 'payment order'
    target_ru = 'очередность платежа'
    description = 'value must be in {1, 2, 3, 4, 5}'
    description_ru = 'значение должно быть одним из {1, 2, 3, 4, 5}'


class OperationKindValidationError(VityaDescribedError, PydanticValueError):
    target = 'operation kind'
    target_ru = 'вид операции'
    description = 'base error'
    description_ru = 'базовая ошибка'


class OperationKindValidationTypeError(OperationKindValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должен быть строкой'


class OperationKindValidationBudgetValueError(OperationKindValidationError):
    description = 'ior budget must be one of {"01", "02", "06"}'
    description_ru = 'для бюджетных операций значение должно быть одним из {"01", "02", "06"}'


class OperationKindValidationValueError(OperationKindValidationBudgetValueError):
    description = 'value must be str with len 2'
    description_ru = 'значение должно быть длиной 2 символов'


class PurposeCodeValidationError(VityaDescribedError, PydanticValueError):
    target = 'purpose code'
    target_ru = 'код назначения'
    description = 'base error'
    description_ru = 'базовая ошибка'


class PurposeCodeValidationTypeError(PurposeCodeValidationError, PydanticTypeError):
    description = 'must be int'
    description_ru = 'должен быть числом'


class PurposeCodeValidationNullError(PurposeCodeValidationError):
    description = 'for non fl payment value must be null'
    description_ru = 'должен отсутствовать для не ФЛ платежей'


class PurposeCodeValidationFlError(PurposeCodeValidationError):
    description = 'for fl payment value must be in {1, 2, 3, 4, 5}'
    description_ru = 'для ФЛ платежей должен быть одним из {1, 2, 3, 4, 5}'


class UINValidationError(VityaDescribedError, PydanticValueError):
    target = 'uin'
    target_ru = 'УИН'
    description = 'base error'
    description_ru = 'базовая ошибка'


class UINValidationTypeError(UINValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должен быть строкой'


class UINValidationLenError(UINValidationError):
    description = 'len must be 4, 20 or 25 len'
    description_ru = 'длина должна быть 4, 20 или 25 символов'


class UINValidationDigitsOnlyError(UINValidationError):
    description = 'must contains only digits'
    description_ru = 'должен содержать только числа'


class UINValidationControlSumError(UINValidationError):
    description = 'control sum error'
    description_ru = 'некорректная контрольная сумма'


class UINValidationValueZeroError(UINValidationError):
    description = 'value cannot be zero'
    description_ru = 'значение не может быть нулем'


class UINValidationBOLenError(UINValidationLenError):
    description = 'len uin for bo payment must be 4, 20 or 25 len'
    description_ru = 'длина для платежей с типом иные должна быть 4, 30 или 25'


class UINValidationBOValueError(UINValidationError):
    description = (
        'for bo payment with payee account start with '
        "('03212', '03222', '03232', '03242', '03252', '03262', '03272') uin must be non zero"
    )
    description_ru = (
        'для платежей с типом иные номер счета получателя должно начинаться с '
        "('03212', '03222', '03232', '03242', '03252', '03262', '03272') и ЮИН должен быть не нулевым"
    )


class UINValidationFNSValueError(UINValidationError):
    description = 'FNS base error'
    description_ru = 'базовая ФНС ошибка'


class UINValidationFNSValueZeroError(UINValidationFNSValueError):
    description = (
        'for FNS with payer status = "13" and empty inn uin must be non zero'
    )
    description_ru = (
        'для платежей в ФНС со статусом плательщика "13" и пустым ИНН, УИН должен быть не нулевым'
    )


class UINValidationFNSNotValueZeroError(UINValidationFNSValueError):
    description = 'for FNS with payer status = "02" uin must be zero'
    description_ru = 'для платежей в ФНС со статусом плательщика "02" и пустым ИНН, УИН должен быть нулевым'


class UINValidationFNSLenError(UINValidationLenError):
    description = 'invalid uin: len uin for FNS payment must be 20 or 25 len'
    description_ru = 'длина УИН для платежей в ФНС должна быть 20 или 15 символов'


class UINValidationOnlyZeroError(UINValidationError):
    description = 'cannot contains only 0 chars'
    description_ru = 'не может состоять только из нулей'


class PurposeValidationError(VityaDescribedError, PydanticValueError):
    target = 'purpose'
    target_ru = 'назначение'
    description = 'base error'
    description_ru = 'базовая ошибка'


class PurposeValidationTypeError(PurposeValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должно быть строкой'


class PurposeValidationMaxLenError(PydanticValueError):
    description = 'len can be from 1 to 210 chars'
    description_ru = 'длина должна быть от 1 до 210 символов'


class PurposeValidationCharactersError(PurposeValidationError):
    description = f'can only consist of {CHARS_FOR_PURPOSE}'
    description_ru = f'может состоять только из символов {CHARS_FOR_PURPOSE}'


class PurposeValidationIPNDSError(PurposeValidationError):
    description = 'for IP payment purpose must contains "НДС"'
    description_ru = 'для платежей ИП назначение должно содержать "НДС"'


class PayerINNValidationCustomsLen10Error(INNValidationLenError):
    description = 'for customs payment and payer status "06", inn must be 10'
    description_ru = 'для платежей в таможню и со статусом плательщика "06" ИНН должно быть "10"'


class PayerINNValidationCustomsLen12Error(INNValidationLenError):
    description = 'for customs payment and payer status 16 or 17, inn must be 12'
    description_ru = 'для платежей таможню со статусом плательщика "16" или "17", значение ИНН должно быть "12"'


class PayerINNValidationEmptyNotAllowedError(INNValidationError):
    description = 'inn cannot be empty'
    description_ru = 'не может быть пустым'


class PayerINNValidationStartWithZerosError(INNValidationError):
    description = 'cannot start with "00"'
    description_ru = 'не может начинаться с "00"'


class PayerINNValidationFiveOnlyZerosError(INNValidationError):
    description = 'inn with len 5 cannot be contains only zeros'
    description_ru = 'ИНН с длиной 5 символов не может содержать только нули'


class PayeeINNValidationNonEmptyError(INNValidationError):
    target_ru = 'payee inn'
    target = 'ИНН получателя'
    description = 'cannot be empty'
    description_ru = 'не может быть пустым'


class PayeeINNValidationFLenError(INNValidationLenError):
    description = 'for fl payee inn must be 12'
    description_ru = 'для платежей ИП ИНН получателя должно быть длиной 12 символов'


class PayeeINNValidationFLLenError(INNValidationLenError):
    description = 'for fl payee inn must be empty or 12 chars'
    description_ru = 'для платежей ИП ИНН получателя должно быть пустым или содержать 12 символов'


class PayeeINNValidationIPLenError(INNValidationError):
    description = 'for ip payee inn must be 12'
    description_ru = 'для платежей ИП ИНН получателя должно быть 12 символов'


class PayeeINNValidationLELenError(INNValidationError):
    description = 'for fns, customs, bo and le inn must be 10'
    description_ru = 'для платежей в бюджет и платежей ЮЛ, ИНН должно быть 10 символов'


class PayerAccountValidationError(VityaDescribedError, PydanticValueError):
    target = 'payer account'
    target_ru = 'счет плательщика'
    description = 'base error'
    description_ru = 'базовая ошибка'


class PayeeAccountValidationError(VityaDescribedError, PydanticValueError):
    target = 'payee account'
    target_ru = 'счет получателя'
    description = 'base error'
    description_ru = 'базовая ошибка'


class PayeeAccountValidationNonEmptyError(PayeeAccountValidationError):
    description = 'cannot be empty'
    description_ru = 'не может быть пустым'


class PayeeAccountValidationLenError(PayeeAccountValidationError):
    description = 'must be 20 digits'
    description_ru = 'должен состоять из 20 цифр'


class PayeeAccountValidationFNSValueError(PayeeAccountValidationError):
    description = 'for FNS payment account must be "03100643000000018500"'
    description_ru = 'для платежей в ФНС счет должен быть "03100643000000018500"'


class AccountNumberValidationError(VityaDescribedError, PydanticValueError):
    target = 'account number'
    target_ru = 'номер счета'
    description = 'base error'
    description_ru = 'базовая ошибка'


class AccountNumberValidationTypeError(AccountNumberValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должен быть строкой'


class AccountNumberValidationSizeError(AccountNumberValidationError):
    description = 'must consist of 20 chars'
    description_ru = 'должен состоять из 20 символов'


class AccountNumberValidationDigitsOnlyError(AccountNumberValidationError):
    description = 'must be only digits'
    description_ru = 'должен состоять только из цифр'


class AccountValidationBICValueError(AccountNumberValidationError):
    description = 'account is not valid for bic'
    description_ru = 'не ключуется с БИКом'


class PayeeAccountValidationBICValueError(AccountValidationBICValueError, PayeeAccountValidationError):
    pass


class PayerStatusValidationError(VityaDescribedError, PydanticValueError):
    target = 'payer status'
    target_ru = 'статус плательщика'
    description = 'base error'
    description_ru = 'базовая ошибка'


class PayerStatusValidationTypeError(PayerStatusValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должен быть строкой'


class PayerStatusValidationValueError(PayerStatusValidationError):
    description = f'value can be only {PAYER_STATUSES}'
    description_ru = f'должен быть одним из {PAYER_STATUSES}'


class PayerStatusValidationNullNotAllowedError(PayerStatusValidationError):
    description = 'for budget payments empty value is not allowed'
    description_ru = 'для платежей в бюджет значение не должно быть пустым'


class PayerStatusValidationCustoms05NotAllowedError(PayerStatusValidationError):
    description = 'for customs payment and for_third_face = true value "06" not allowed'
    description_ru = 'для платежей в таможню и для платежей за третьих лиц значение статуса не может быть "06"'


class KPPValidationOnlyEmptyError(KPPValidationError):
    description = 'only empty is allowed'
    description_ru = 'должно быть пустым'


class KPPValidationEmptyNotAllowed(KPPValidationError):
    description = 'empty value is not allowed'
    description_ru = 'пустое значение не разрешено'


class PayerKPPValidationError(KPPValidationError):
    target = 'payer kpp'
    target_ru = 'КПП плательщика'
    description = 'ase error'
    description_ru = 'базовая ошибка'


class PayerKPPValidationOnlyEmptyError(PayerKPPValidationError, KPPValidationOnlyEmptyError):
    description = 'for ip, fl or le value must be empty'
    description_ru = 'для платежей ИП, ФЛ, И ЮЛ значение должно быть пустым'


class PayerKPPValidationINN10EmptyNotAllowed(PayerKPPValidationError, KPPValidationEmptyNotAllowed):
    description = 'for budget payment with inn = 10 inn empty value is not allowed'
    description_ru = 'для платежей в бюджет с ИНН = "10" значение КПП должно быть заполнено'


class PayerKPPValidationINN12OnlyEmptyError(PayerKPPValidationOnlyEmptyError):
    description = 'for budget with inn = 12 only empty allowed'
    description_ru = 'для платежей в бюджет с ИНН = "10" значение КПП должно быть пустым'


class PayeeKPPValidationError(KPPValidationError):
    target = 'payee kpp'
    target_ru = 'КПП получателя'
    description = 'base error'
    description_ru = 'базовая ошибка'


class PayeeKPPValidationOnlyEmptyError(PayeeKPPValidationError, KPPValidationOnlyEmptyError):
    description = 'for ip or fl only empty allowed'
    description_ru = 'для платежей ИП и ФЛ значение должно быть пустым'


class PayeeKPPValidationEmptyNotAllowed(PayeeKPPValidationError, KPPValidationEmptyNotAllowed):
    description = 'for fns, customs, budget other or le empty value is not allowed'
    description_ru = 'для платежей в бюджет или платежей ЮЛ пустое значение недопустимо'


class PayeeKPPValidationStartsWithZeros(PayeeKPPValidationError):
    description = 'for fns, customs, budget other or le kpp cannot starts with "00"'
    description_ru = 'для платежей в бюджет или платежей ЮЛ значение не может начинаться с "00"'


class CBCValidationError(VityaDescribedError, PydanticValueError):
    target = 'CBC'
    target_ru = 'КБК'
    description = 'base error'
    description_ru = 'базовая ошибка'


class CBCValidationTypeError(CBCValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должен быть строкой'


class CBCValidationEmptyNotAllowed(CBCValidationError):
    description = 'for fns or customs empty value is not allowed'
    description_ru = 'для платежей в ФНС или таможню значение не должно быть пустым'


class CBCValidationValueLenError(CBCValidationError):
    description = 'must be 20 digits'
    description_ru = 'должен состоять из 20 цифр'


class CBCValidationValueDigitsOnlyError(CBCValidationError):
    description = 'only digits are allowed'
    description_ru = 'должен состоять только из цифр'


class CBCValidationValueCannotZerosOnly(CBCValidationError):
    description = 'cannot contain only zeros'
    description_ru = 'не может состоять только из нулей'


class OKTMOValidationEmptyNotAllowed(OKTMOValidationError):
    target = 'oktmo'
    target_ru = 'ОКТМО'
    description = 'empty value is not allowed'
    description_ru = 'значение не должно быть пустым'


class OKTMOValidationFNSEmptyNotAllowed(OKTMOValidationEmptyNotAllowed):
    description = 'invalid oktmo: for fns with payer status = "02" empty value is not allowed'
    description_ru = 'для платежей в фнс со статусом плательщика "02" значение не может быть пустым'


class OKTMOValidationZerosNotAllowed(OKTMOValidationError):
    description = 'cannot be all zeros'
    description_ru = 'не может состоять полностью из нулей'


class ReasonValidationError(VityaDescribedError, PydanticValueError):
    target = 'reason'
    target_ru = 'основание платежа'
    description = 'base error'
    description_ru = 'базовая ошибка'


class ReasonValidationTypeError(ReasonValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должно быть строкой'


class ReasonValidationFNSOnlyEmptyError(ReasonValidationError):
    description = 'for fns only empty allowed'
    description_ru = 'для платежей в ФНС значение должно быть пустым'


class ReasonValidationValueLenError(ReasonValidationError):
    description = 'must be 2 chars'
    description_ru = 'должно состоять из 2 символов'


class ReasonValidationValueErrorCustoms(ReasonValidationError):
    description = f'for customs payment value must be in {CUSTOMS_REASONS}'
    description_ru = f'для платежей в таможню значение должно быть одним из {CUSTOMS_REASONS}'


class TaxPeriodValidationError(VityaDescribedError, PydanticValueError):
    target = 'tax period'
    target_ru = 'Периодичность платежа / Код таможенного органа'
    description = 'base error'
    description_ru = 'базовая ошибка'


class TaxPeriodValidationTypeError(TaxPeriodValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должно быть строкой'


class TaxPeriodValidationEmptyNotAllowed(TaxPeriodValidationError):
    description = 'empty is not allowed'
    description_ru = 'значение не должно быть пустым'


class TaxPeriodValidationValueLenError(TaxPeriodValidationError):
    description = 'invalid len'
    description_ru = 'некорректная длина'


class TaxPeriodValidationBOValueLenError(TaxPeriodValidationValueLenError):
    description = 'for bo must be 10'
    description_ru = 'для иных платежей в бюджет длина должны быть равна 10'


class TaxPeriodValidationCustomsEmptyNotAllowed(TaxPeriodValidationEmptyNotAllowed):
    pass


class TaxPeriodValidationCustomsValueLenError(TaxPeriodValidationValueLenError):
    description = 'for customs len must be 8'
    description_ru = 'для платежей в таможню длина должна быть 8 символов'


class TaxPeriodValidationFNS02EmptyNotAllowed(TaxPeriodValidationError):
    description = 'for fns with payer status = "02" empty is not allowed'
    description_ru = 'для платежей в ФНС со статусом плательщика "02" пустое значение недопустимо'


class TaxPeriodValidationFNS01OnlyEmpty(TaxPeriodValidationError):
    description = 'for fns with payer status = "01" or "13" only empty allowed'
    description_ru = 'для платежей в ФНС со статусом плательщика "01" или "13" значение должно быть пустым'


class TaxPeriodValidationFNSEmptyNotAllowed(TaxPeriodValidationEmptyNotAllowed):
    description = 'for fns empty is not allowed'
    description_ru = 'для платежей в ФНС пустое значение недопустимо'


class TaxPeriodValidationFNSValueLenError(TaxPeriodValidationValueLenError):
    description = 'for fns len must be 10 chars'
    description_ru = 'для платежей в ФНС длина значения должна быть 10 символов'


class DocumentNumberValidationError(VityaDescribedError, PydanticValueError):
    target = 'document number'
    target_ru = 'номер документа'
    description = 'base error'
    description_ru = 'базовая ошибка'


class DocumentNumberValidationTypeError(DocumentNumberValidationError, PydanticTypeError):
    description = 'must be a str'
    description_ru = 'должен быть строкой'


class DocumentNumberValidationOnlyEmptyError(DocumentNumberValidationError):
    description = 'only empty allowed'
    description_ru = 'должно быть пустым'


class DocumentNumberValidationEmptyNotAllowed(DocumentNumberValidationError):
    description = 'empty is not allowed'
    description_ru = 'значение не должно быть пустым'


class DocumentNumberValidationFNSOnlyEmptyError(DocumentNumberValidationOnlyEmptyError):
    description = 'for fns only empty allowed'
    description_ru = 'для платежей в ФНС значение должно быть пустым'


class DocumentNumberValidationBOEmptyNotAllowed(DocumentNumberValidationEmptyNotAllowed):
    description = 'for bo with payer status = "24", empty payer inn and empty uin empty is not allowed'
    description_ru = (
        'для иных платежей в бюджет со статусом плательщика "24", пустое значение ИНН плательщика и УИН недопустимо'
    )


class DocumentNumberValidationBOOnlyEmptyError(DocumentNumberValidationOnlyEmptyError):
    description = (
        'for bo with payee account starts with "03212",'
        ' payer status = "31", uin is not empty - empty value is not allowed'
    )
    description_ru = (
        'для иных платежей в бюджет счет получателя должен начинаться с "03212",'
        ' статус плательщика должен быть "31, а УИН быть заполнен'
    )


class DocumentNumberValidationBOValueError(DocumentNumberValidationError):
    description = f'for bo first two chars should be in {DOCUMENT_NUMBERS}, and third is equal to ";"'
    description_ru = (
        f'для иных платежей в бюджет первые два символы должны быть в {DOCUMENT_NUMBERS},'
        f' а третий символ должен быть равен ";"'
    )


class DocumentNumberValidationBOValueLenError(DocumentNumberValidationError):
    description = 'for bo value len max 15'
    description_ru = 'для иных платежей в бюджет максимальная длина должна быть равна 15'


class DocumentNumberValidationCustoms00ValueError(DocumentNumberValidationError):
    description = 'for customs with reason = "00" value must starts with "00"'
    description_ru = 'для платежей в таможню основание платежа должно быть равно "00", а номер должен начинаться с "00"'


class DocumentNumberValidationCustomsValueLen7Error(DocumentNumberValidationError):
    description = 'for customs with reason in {"ПК", "УВ", "ТГ", "ТБ", "ТД", "ПВ"} value len max 7'
    description_ru = (
        'для платежей в таможню с основанием платежа в {"ПК", "УВ", "ТГ", "ТБ", "ТД", "ПВ"}'
        ' длина значения должна быть не более 7 символов'
    )


class DocumentNumberValidationCustomsValueLen15Error(DocumentNumberValidationError):
    description = 'for customs with reason in {"ИЛ", "ИН", "ПБ", "КЭ"} value len from 1 to 15 chars'
    description_ru = (
        'для платежей в таможню с основанием платежа в {"ИЛ", "ИН", "ПБ", "КЭ"}'
        ' длина значения должна быть от 1 до 15 символов'
    )


class DocumentDateValidationError(VityaDescribedError, PydanticValueError):
    target = 'document date'
    target_ru = 'дата документа'
    description = 'base error'
    description_ru = 'базовая ошибка'


class DocumentDateValidationTypeError(DocumentDateValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должна быть строкой'


class DocumentDateValidationFNSOnlyEmptyError(DocumentDateValidationError):
    description = 'for fns only empty allowed'
    description_ru = 'для платежей в ФНС значение должно быть пустым'


class DocumentDateValidationCustomsLenError(DocumentDateValidationError):
    description = 'for customs value must be equal 10 chars'
    description_ru = 'для платежей в таможню длина значения должна быть 10 символов'


class DocumentDateValidationBOLenError(DocumentDateValidationError):
    description = 'for bo value max 10 chars'
    description_ru = 'для иных платежей в бюджет значение не должно быть длиннее 10 символов'
