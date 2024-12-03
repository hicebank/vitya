from datetime import date
from typing import Any

from pydantic.errors import PydanticTypeError, PydanticValueError

from vitya.errors import (
    INNValidationError,
    INNValidationLenError,
    KPPValidationError,
    OKTMOValidationError,
)
from vitya.errors_base import (
    ExactFieldLenError,
    IncorrectData,
    IncorrectLen,
    NeedRequiredField,
    VityaDescribedError,
)
from vitya.payment_order.enums import PaymentType
from vitya.payment_order.payments.constants import (
    CHANGE_YEAR,
    CUSTOMS_REASONS,
    DOCUMENT_NUMBERS,
    FNS_KPP,
    FTS_KPP,
    FTS_OKTMO,
    PAYER_STATUSES,
    PAYER_STATUSES_AFTER_2024,
)


class PaymentTypeValueError(VityaDescribedError, PydanticValueError):
    target = 'payment type'
    target_ru = 'Тип платежа'
    description = 'неизвестный тип платежа '
    description_ru = 'неизвестный тип платежа '

    def __init__(self, payment_type: PaymentType, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
        super().__init__(*args, **kwargs)
        self.description += payment_type.name
        self.description_ru += payment_type.name_ru


class AmountValidationError(VityaDescribedError, PydanticValueError):
    target = 'amount'
    target_ru = 'Сумма'
    description = 'base error'
    description_ru = 'базовая ошибка'


class AmountValidationLengthError(AmountValidationError, IncorrectLen):
    description = 'str representation cannot contains more 18 chars'
    description_ru = 'строковое представление не может содержать более 18 символов'


class AmountValidationLessOrEqualZeroError(AmountValidationError, IncorrectData):
    description = 'cannot be less than or equal to 0.0'
    description_ru = 'не может быть меньше или равно 0.0'


class AmountNotANumber(AmountValidationError, IncorrectData):
    description = 'require to be a number'
    description_ru = 'должно быть числом'


class CustomerValidationError(VityaDescribedError, PydanticValueError):
    target = 'customer'
    target_ru = 'Плательщик или Получатель'
    description = 'base error'
    description_ru = 'базовая ошибка'


class CustomerValidationSizeError(CustomerValidationError):
    description = 'name must sized from 1 to 160 chars'
    description_ru = 'длина имени должно быть между 1 и 160 символами'


class PayerValidationError(CustomerValidationError):
    target = 'payer'
    target_ru = 'Плательщик'


class PayerValidationSizeError(PayerValidationError, CustomerValidationSizeError, IncorrectLen):
    pass


class ReceiverValidationError(CustomerValidationError):
    target = 'receiver'
    target_ru = 'Получатель'


class ReceiverValidationSizeError(ReceiverValidationError, CustomerValidationSizeError, IncorrectLen):
    pass


class ReceiverValidationNameError(ReceiverValidationError, IncorrectData):
    description = 'contains account number'
    description_ru = 'содержит номер счета'


class NumberValidationLenError(PydanticValueError, IncorrectLen):
    target = 'number'
    target_ru = 'Номер'
    description = 'cannot be longer than 6 chars'
    description_ru = 'не может быть длиннее 6 символов'


class PaymentOrderValidationError(VityaDescribedError, PydanticValueError):
    target = 'payment order'
    target_ru = 'Очередность платежа'
    description = 'value must be in {1, 2, 3, 4, 5}'
    description_ru = 'значение должно быть одним из {1, 2, 3, 4, 5}'


class PaymentOrderLenError(PaymentOrderValidationError, ExactFieldLenError):
    required_len = 1


class OperationKindValidationError(VityaDescribedError, PydanticValueError):
    target = 'operation kind'
    target_ru = 'Вид операции'
    description = 'base error'
    description_ru = 'базовая ошибка'


class OperationKindValidationTypeError(OperationKindValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должен быть строкой'


class OperationKindValidationBudgetValueError(OperationKindValidationError):
    description = 'ior budget must be one of {"01", "02", "06"}'
    description_ru = 'для бюджетных операций значение должно быть одним из {"01", "02", "06"}'


class OperationKindValidationValueError(OperationKindValidationBudgetValueError, ExactFieldLenError):
    description = 'value must be str with len 2'
    description_ru = 'значение должно быть длиной 2 символов'
    required_len = 2


class PurposeCodeValidationError(VityaDescribedError, PydanticValueError):
    target = 'purpose code'
    target_ru = 'Код назначения'
    description = 'base error'
    description_ru = 'базовая ошибка'


class PurposeCodeValidationTypeError(PurposeCodeValidationError, PydanticTypeError):
    description = 'must be int'
    description_ru = 'должен быть числом'


class PurposeCodeValidationNullError(PurposeCodeValidationError):
    description = 'for non fl payment value must be null'
    description_ru = 'должен отсутствовать для не ФЛ платежей и не хамелеона'


class PurposeCodeValidationFlError(PurposeCodeValidationError):
    description = 'for fl payment value must be in {1, 2, 3, 4, 5} or must be empty'
    description_ru = 'для платежей ФЛ должен быть одним из {1, 2, 3, 4, 5} или быть пустым'


class PurposeCodeValidationChameleonError(PurposeCodeValidationError):
    description = 'for chameleon payment value must be in {1, 2, 3, 4, 5} or must be empty'
    description_ru = 'для платежей хамелеону должен быть одним из {1, 2, 3, 4, 5} или быть пустым'


class PurposeValidationForThirdPersonError(PurposeCodeValidationError):
    description = 'for third person purpose must match pattern inn//name//purpose'
    description_ru = 'для платежей за третьих лиц назначение должно соответствовать шаблону ИНН//ФИО//Назначение'


class UINValidationError(VityaDescribedError, PydanticValueError):
    target = 'uin'
    target_ru = 'УИН'
    description = 'base error'
    description_ru = 'базовая ошибка'


class UINValidationTypeError(UINValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должен быть строкой'


class UINValidationLenError(UINValidationError, IncorrectLen):
    description = 'len must be 4, 20 or 25 len'
    description_ru = 'длина должна быть 4, 20 или 25 символов'


class UINValidationDigitsOnlyError(UINValidationError, IncorrectData):
    description = 'must contains only digits'
    description_ru = 'должен содержать только числа'


class UINValidationControlSumError(UINValidationError, IncorrectData):
    description = 'control sum error'
    description_ru = 'некорректная контрольная сумма'


class UINValidationValueZeroError(UINValidationError, NeedRequiredField):
    description = 'value cannot be zero'
    description_ru = 'значение не может быть нулем'


class UINValidationValueBudget33PayerStatusIncorrectLength(UINValidationError, NeedRequiredField):
    description = 'value cannot consist of zeros and be of any length aprt from 20 or 25 if payer status is 33'
    description_ru = 'значение не может состоять из нулей и быть любой длины кроме 20 или 25 если статус плательщика 33'


class UINValidationBOLenError(UINValidationLenError):
    description = 'len uin for bo payment must be 4, 20 or 25 len'
    description_ru = 'длина для платежей с типом иные должна быть 4, 30 или 25'


class UINValidationFNSValueError(UINValidationError):
    description = 'FNS base error'
    description_ru = 'базовая ФНС ошибка'


class UINValidationFNSValueZeroError(UINValidationFNSValueError, NeedRequiredField):
    description = (
        'for FNS with payer status = "13" and empty inn uin must be non zero'
    )
    description_ru = (
        'для платежей в ФНС со статусом плательщика "13" и пустым ИНН, УИН должен быть не нулевым'
    )


class UINValidationFNSNotValueZeroError(UINValidationFNSValueError, IncorrectData):
    description = 'for FNS with payer status = "02" uin must be zero'
    description_ru = 'для платежей в ФНС со статусом плательщика "02" и пустым ИНН, УИН должен быть нулевым'


class UINValidationBONotEmpty(UINValidationFNSValueError, NeedRequiredField):
    description = 'for budget other and receiver number starting with 03212 uin must be filled'
    description_ru = (
        'для платежей в бюджет иные с номером счёта получателя, который начинается с "03212", УИН должен быть заполен'
    )


class UINValidationFNSOrFTSLenError(UINValidationLenError):
    description = 'invalid uin: len uin for FNS or FTS payment must be 20 or 25 len'
    description_ru = 'длина УИН для платежей в ФНС или ФТС должна быть 20 или 15 символов'


class UINValidationOnlyZeroError(UINValidationError, IncorrectData):
    description = 'cannot contains only 0 chars'
    description_ru = 'не может состоять только из нулей'


class PurposeValidationError(VityaDescribedError, PydanticValueError):
    target = 'purpose'
    target_ru = 'Назначение'
    description = 'base error'
    description_ru = 'базовая ошибка'


class PurposeValidationTypeError(PurposeValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должно быть строкой'


class PurposeValidationMaxLenError(PurposeValidationError, IncorrectLen):
    description = 'len can be from 1 to 210 chars'
    description_ru = 'длина должна быть от 1 до 210 символов'


class PurposeValidationValueEmptyErrorForNonFNS(PurposeValidationError, NeedRequiredField):
    description = 'value cannot be empty for non FNS payments'
    description_ru = 'значение не может быть пустым для платежей не в ФНС'


class PayerINNValidationError(INNValidationError):
    target = 'payer inn'
    target_ru = 'ИНН плательщика'


class PayerINNValidationCustomsLen10Error(INNValidationLenError, PayerINNValidationError, ExactFieldLenError):
    description = 'for customs payment and payer status "06", inn must be 10'
    description_ru = 'для платежей в таможню и со статусом плательщика "06" ИНН должно быть быть длиной 10 символов'
    required_len = 10


class PayerINNValidationCustomsLen12Error(INNValidationLenError, PayerINNValidationError, ExactFieldLenError):
    description = 'for customs payment and payer status 16 or 17, inn must be 12'
    description_ru = (
        'для платежей таможню со статусом плательщика "16" или "17",'
        ' значение ИНН должно быть длиной 12 символов'
    )
    required_len = 12


class PayerINNValidationEmptyNotAllowedError(PayerINNValidationError, NeedRequiredField):
    description = 'inn cannot be empty'
    description_ru = 'не может быть пустым'


class PayerINNValidationStartWithZerosError(PayerINNValidationError, IncorrectData):
    description = 'cannot start with "00"'
    description_ru = 'не может начинаться с "00"'


class ReceiverINNValidationError(INNValidationError):
    target = 'receiver inn'
    target_ru = 'ИНН получателя'


class ReceiverINNValidationNonEmptyError(ReceiverINNValidationError, NeedRequiredField):
    description = 'cannot be empty'
    description_ru = 'не может быть пустым'


class ReceiverINNValidationFLenError(ReceiverINNValidationError, ExactFieldLenError):
    required_len = 12
    description = 'for fl receiver inn must be 12'
    description_ru = 'для платежей ИП ИНН получателя должно быть длиной 12 символов'


class ReceiverINNValidationFLLenError(ReceiverINNValidationError, ExactFieldLenError):
    required_len = 12
    description = 'for fl receiver inn must be empty or 12 chars'
    description_ru = 'для платежей ИП ИНН получателя должно быть пустым или содержать 12 символов'


class ReceiverINNValidationChameleonLenError(INNValidationLenError, ReceiverINNValidationError):
    description = 'for chameleon receiver inn must be empty or 12 or 10 chars'
    description_ru = 'для платежей Хамелеону ИНН получателя должно быть пустым или содержать 12 или 10 символов'


class ReceiverINNValidationIPLenError(ReceiverINNValidationError, ExactFieldLenError):
    required_len = 12
    description = 'for ip receiver inn must be 12'
    description_ru = 'для платежей ИП ИНН получателя должно быть 12 символов'


class ReceiverINNValidationLELenError(ReceiverINNValidationError, ExactFieldLenError):
    required_len = 10
    description = 'for fns, customs, bo and le inn must be 10'
    description_ru = 'для платежей в бюджет и платежей ЮЛ, ИНН должно быть 10 символов'


class ReceiverAccountValidationError(VityaDescribedError, PydanticValueError):
    target = 'receiver account'
    target_ru = 'Счет получателя'
    description = 'base error'
    description_ru = 'базовая ошибка'


class ReceiverAccountValidationNonEmptyError(ReceiverAccountValidationError):
    description = 'cannot be empty'
    description_ru = 'не может быть пустым'


class ReceiverAccountValidationLenError(ReceiverAccountValidationError):
    description = 'must be 20 digits'
    description_ru = 'должен состоять из 20 цифр'


class ReceiverAccountValidationFNSValueError(ReceiverAccountValidationError, IncorrectData):
    description = 'for FNS payment account must be "03100643000000018500"'
    description_ru = 'для платежей в ФНС счет должен быть "03100643000000018500"'


class AccountNumberValidationError(VityaDescribedError, PydanticValueError):
    target = 'account number'
    target_ru = 'Номер счета'
    description = 'base error'
    description_ru = 'базовая ошибка'


class AccountNumberValidationTypeError(AccountNumberValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должен быть строкой'


class AccountNumberValidationSizeError(AccountNumberValidationError, ExactFieldLenError):
    description = 'must consist of 20 chars'
    description_ru = 'должен состоять из 20 символов'
    required_len = 20


class AccountNumberValidationDigitsOnlyError(AccountNumberValidationError):
    description = 'must be only digits'
    description_ru = 'должен состоять только из цифр'


class AccountValidationBICValueError(AccountNumberValidationError):
    description = 'account is not valid for bic'
    description_ru = 'не ключуется с БИКом'


class ReceiverAccountNumberValidationTypeError(
    ReceiverAccountValidationError,
    AccountNumberValidationTypeError,
):
    pass


class ReceiverAccountNumberValidationSizeError(
    ReceiverAccountValidationError,
    AccountNumberValidationSizeError,
):
    pass


class ReceiverAccountNumberValidationDigitsOnlyError(
    ReceiverAccountValidationError,
    AccountNumberValidationDigitsOnlyError,
    IncorrectData
):
    pass


class ReceiverAccountValidationBICValueError(
    ReceiverAccountValidationError,
    AccountValidationBICValueError,
    IncorrectData,
):
    pass


class ReceiverAccountValidationCustomsValueError(
    ReceiverAccountValidationError,
    IncorrectData
):
    description = 'for customs payment account must be "03100643000000019502"'
    description_ru = 'для платежей в таможню счет должен быть "03100643000000019502"'


class PayerStatusValidationError(VityaDescribedError, PydanticValueError):
    target = 'payer status'
    target_ru = 'Статус плательщика'
    description = 'base error'
    description_ru = 'базовая ошибка'


class PayerStatusValidationTypeError(PayerStatusValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должен быть строкой'


class PayerStatusValidationValueError(PayerStatusValidationError):
    description = f'value can be only {PAYER_STATUSES if date.today().year < CHANGE_YEAR else PAYER_STATUSES_AFTER_2024}'
    description_ru = f'должен быть одним из {PAYER_STATUSES if date.today().year < CHANGE_YEAR else PAYER_STATUSES_AFTER_2024}'


class PayerStatusValidationNullNotAllowedError(PayerStatusValidationError):
    description = 'for budget payments empty value is not allowed'
    description_ru = 'для платежей в бюджет значение не должно быть пустым'


class PayerStatusValidationCustoms05NotAllowedError(PayerStatusValidationError, IncorrectData):
    description = 'for customs payment and for_third_face = true value "06" not allowed'
    description_ru = 'для платежей в таможню и для платежей за третьих лиц значение статуса не может быть "06"'


class PayerStatusValidationCustomsIncorrectDataError(PayerStatusValidationError, IncorrectData):
    description = 'for customs payment only values "06", "16", "17", "28", "30" are allowed'
    description_ru = 'для платежей в таможню значение статуса может быть только "06", "16", "17", "28", "30"'


class PayerStatusValidationFNSIncorrectDataError(PayerStatusValidationError, IncorrectData):
    description = 'for fns payment only values "01", "13" are allowed'
    description_ru = 'для платежей в налоговую значение статуса может быть только "01", "13"'


class PayerStatusValidationOtherIncorrectDataError(PayerStatusValidationError, IncorrectData):
    description = 'for other payment values "01", "13", "06", "16", "17", "28", "30" not allowed'
    description_ru = (
        'для платежей в иные организации значение статуса не может быть "01", "13", "06", "16", "17", "28", "30"'
    )


class KPPValidationOnlyEmptyError(KPPValidationError):
    description = 'only empty is allowed'
    description_ru = 'должно быть пустым'


class KPPValidationEmptyNotAllowed(KPPValidationError):
    description = 'empty value is not allowed'
    description_ru = 'пустое значение не разрешено'


class PayerKPPValidationError(KPPValidationError):
    target = 'payer kpp'
    target_ru = 'КПП плательщика'
    description = 'base error'
    description_ru = 'базовая ошибка'


class PayerKPPValidationOnlyEmptyError(PayerKPPValidationError, KPPValidationOnlyEmptyError):
    description = 'for ip, fl or le value must be empty'
    description_ru = 'для платежей ИП, ФЛ, И ЮЛ значение должно быть пустым'


class PayerKPPValidationINN10EmptyNotAllowed(PayerKPPValidationError, KPPValidationEmptyNotAllowed, NeedRequiredField):
    description = 'for budget payment with inn length 10 kpp empty value is not allowed'
    description_ru = 'для платежей в бюджет с длиной ИНН равной 10 значение КПП должно быть заполнено'


class PayerKPPValidationINN12OnlyEmptyError(PayerKPPValidationOnlyEmptyError, IncorrectData):
    description = 'for budget with inn length 12 kpp only empty allowed'
    description_ru = 'для платежей в бюджет с длиной ИНН равной 12 значение КПП должно быть пустым'


class PayerKPPValidationINN5EmptyNotAllowed(PayerKPPValidationError, KPPValidationEmptyNotAllowed, NeedRequiredField):
    description = 'for budget payment with inn length 5 kpp empty value is not allowed'
    description_ru = 'для платежей в бюджет с длиной ИНН равной 5 значение КПП должно быть заполнено'


class ReceiverKPPValidationError(KPPValidationError):
    target = 'receiver kpp'
    target_ru = 'КПП получателя'
    description = 'base error'
    description_ru = 'базовая ошибка'


class ReceiverKPPValidationOnlyEmptyError(ReceiverKPPValidationError, KPPValidationOnlyEmptyError, IncorrectData):
    description = 'for ip or fl only empty allowed'
    description_ru = 'для платежей ИП и ФЛ значение должно быть пустым'


class ReceiverKPPValidationEmptyNotAllowed(ReceiverKPPValidationError, KPPValidationEmptyNotAllowed):
    description = 'for fns, customs, budget other empty value is not allowed'
    description_ru = 'для платежей в бюджет пустое значение недопустимо'


class ReceiverKPPValidationStartsWithZeros(ReceiverKPPValidationError, IncorrectData):
    description = 'for fns, customs, budget other kpp cannot starts with "00"'
    description_ru = 'для платежей в бюджет значение не может начинаться с "00"'


class ReceiverKPPValidationFNS(ReceiverKPPValidationError, IncorrectData):
    description = f'for fns kpp can only be {FNS_KPP}'
    description_ru = f'для платежей в фнс значение может быть только {FNS_KPP}'


class ReceiverKPPValidationFTS(ReceiverKPPValidationError, IncorrectData):
    description = f'for customs kpp can only be {FTS_KPP}'
    description_ru = f'для платежей в таможню значение может быть только {FTS_KPP}'


class CBCValidationError(VityaDescribedError, PydanticValueError):
    target = 'CBC'
    target_ru = 'КБК'
    description = 'base error'
    description_ru = 'базовая ошибка'


class CBCValidationTypeError(CBCValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должен быть строкой'


class CBCValidationEmptyNotAllowed(CBCValidationError, NeedRequiredField):
    description = 'for fns or customs empty value is not allowed'
    description_ru = 'для платежей в ФНС или таможню значение не должно быть пустым'


class CBCValidationValueLenError(CBCValidationError, ExactFieldLenError):
    description = 'must be 20 digits'
    description_ru = 'должен состоять из 20 цифр'
    required_len = 20


class CBCValidationValueDigitsOnlyError(CBCValidationError, IncorrectData):
    description = 'only digits are allowed'
    description_ru = 'должен состоять только из цифр'


class CBCValidationValueCannotZerosOnly(CBCValidationError, IncorrectData):
    description = 'cannot contain only zeros'
    description_ru = 'не может состоять только из нулей'


class OKTMOValidationEmptyNotAllowed(OKTMOValidationError, NeedRequiredField):
    target = 'oktmo'
    target_ru = 'ОКТМО'
    description = 'empty value is not allowed'
    description_ru = 'значение не должно быть пустым'


class OKTMOValidationFNSEmptyNotAllowed(OKTMOValidationEmptyNotAllowed, NeedRequiredField):
    description = 'invalid oktmo: for fns with payer status = "02" empty value is not allowed'
    description_ru = 'для платежей в фнс со статусом плательщика "02" значение не может быть пустым'


class OKTMOValidationZerosNotAllowed(OKTMOValidationError, IncorrectData):
    description = 'cannot be all zeros'
    description_ru = 'не может состоять полностью из нулей'


class OKTMOValidationFTS(OKTMOValidationError, IncorrectData):
    description = f'for customs payments oktmo can be only {FTS_OKTMO}'
    description_ru = f'для платежей в таможню октмо может быть только {FTS_OKTMO}'


class ReasonValidationError(VityaDescribedError, PydanticValueError):
    target = 'reason'
    target_ru = 'Основание платежа'
    description = 'base error'
    description_ru = 'базовая ошибка'


class ReasonValidationTypeError(ReasonValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должно быть строкой'


class ReasonValidationValueLenError(ReasonValidationError, IncorrectLen):
    description = 'must be 2 chars'
    description_ru = 'должно состоять из 2 символов'


class ReasonValidationValueErrorCustoms(ReasonValidationError, IncorrectData):
    description = f'for customs payment value must be in {CUSTOMS_REASONS}'
    description_ru = f'для платежей в таможню значение должно быть одним из {CUSTOMS_REASONS}'


class ReasonValidationValueErrorFNS(ReasonValidationError, IncorrectData):
    description = 'for fns payment value must be either 0 or empty'
    description_ru = 'для платежей в ФНС значение должно быть 0 или пустым'


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


class TaxPeriodValidationBOValueLenError(TaxPeriodValidationValueLenError, IncorrectLen):
    description = 'for bo must be 10'
    description_ru = 'для иных платежей в бюджет длина должны быть равна 10'


class TaxPeriodValidationCustomsEmptyNotAllowed(TaxPeriodValidationEmptyNotAllowed, NeedRequiredField):
    pass


class TaxPeriodValidationCustomsValueLenError(TaxPeriodValidationValueLenError, ExactFieldLenError):
    description = 'for customs len must be 8'
    description_ru = 'для платежей в таможню длина должна быть 8 символов'
    required_len = 8


class TaxPeriodValidationFNS02EmptyNotAllowed(TaxPeriodValidationError, NeedRequiredField):
    description = 'for fns with payer status = "02" empty is not allowed'
    description_ru = 'для платежей в ФНС со статусом плательщика "02" пустое значение недопустимо'


class TaxPeriodValidationFNS01OnlyEmpty(TaxPeriodValidationError, IncorrectData):
    description = 'for fns with payer status = "01" or "13" only empty allowed'
    description_ru = 'для платежей в ФНС со статусом плательщика "01" или "13" значение должно быть пустым'


class TaxPeriodValidationFNSValueLenError(TaxPeriodValidationValueLenError, ExactFieldLenError):
    description = 'for fns len must be 10 chars'
    description_ru = 'для платежей в ФНС длина значения должна быть 10 символов'
    required_len = 10


class DocumentNumberValidationError(VityaDescribedError, PydanticValueError):
    target = 'document number'
    target_ru = 'Номер документа'
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


class DocumentNumberValidationFNSOnlyEmptyError(DocumentNumberValidationOnlyEmptyError, IncorrectData):
    description = 'for fns only empty allowed'
    description_ru = 'для платежей в ФНС значение должно быть пустым'


class DocumentNumberValidationBOEmptyNotAllowed(DocumentNumberValidationEmptyNotAllowed):
    description = 'for bo with payer status = "24", empty payer inn and empty uin empty is not allowed'
    description_ru = (
        'для иных платежей в бюджет со статусом плательщика "24", пустое значение ИНН плательщика и УИН недопустимо'
    )


class DocumentNumberValidationBOPayerStatus33OnlyEmptyError(DocumentNumberValidationOnlyEmptyError, IncorrectData):
    description = (
        'for bo with payer status = "33" , must be empty'
    )
    description_ru = (
        'для иных платежей в бюджет со статусом плательщика = «33» поле документ должно быть обязательно пустым'
    )


class DocumentNumberValidationBOOnlyEmptyError(DocumentNumberValidationOnlyEmptyError, IncorrectData):
    description = (
        'for bo with receiver account starts with "03212",'
        ' payer status = "31", uin is not empty - empty value is not allowed'
    )
    description_ru = (
        'для иных платежей в бюджет счет получателя должен начинаться с "03212",'
        ' статус плательщика должен быть "31, а УИН быть заполнен'
    )


class DocumentNumberValidationBOValueError(DocumentNumberValidationError, IncorrectData):
    description = (
        f'for bo with tax payer status 24 first two chars should be '
        f'in {DOCUMENT_NUMBERS}, and third is equal to ";"'
    )
    description_ru = (
        f'для иных платежей в бюджет со статусом плательщика 24 первые два символы должны быть в {DOCUMENT_NUMBERS},'
        f' а третий символ должен быть равен ";"'
    )


class DocumentNumberValidationBOValueLenError(DocumentNumberValidationError, IncorrectLen):
    description = 'for bo value len max 15'
    description_ru = 'для иных платежей в бюджет максимальная длина должна быть равна 15'


class DocumentNumberValidationCustoms00ValueError(DocumentNumberValidationError, IncorrectData):
    description = 'for customs with reason = "00" value have to be "00" or "0"'
    description_ru = 'для платежей в таможню основание платежа должно быть равно "00", а номер должен быть "00" или "0"'


class DocumentNumberValidationCustomsValueLen7Error(DocumentNumberValidationError, IncorrectLen):
    description = 'for customs with reason in {"ПК", "УВ", "ТГ", "ТБ", "ТД", "ПВ"} value len max 7'
    description_ru = (
        'для платежей в таможню с основанием платежа в {"ПК", "УВ", "ТГ", "ТБ", "ТД", "ПВ"}'
        ' длина значения должна быть не более 7 символов'
    )


class DocumentNumberValidationCustomsValueLen15Error(DocumentNumberValidationError, IncorrectLen):
    description = 'for customs with reason in {"ИЛ", "ИН", "ПБ", "КЭ"} value len from 1 to 15 chars'
    description_ru = (
        'для платежей в таможню с основанием платежа в {"ИЛ", "ИН", "ПБ", "КЭ"}'
        ' длина значения должна быть от 1 до 15 символов'
    )


class DocumentDateValidationError(VityaDescribedError, PydanticValueError):
    target = 'document date'
    target_ru = 'Дата документа'
    description = 'base error'
    description_ru = 'базовая ошибка'


class DocumentDateValidationTypeError(DocumentDateValidationError, PydanticTypeError):
    description = 'must be str'
    description_ru = 'должна быть строкой'


class DocumentDateValidationFNSOnlyEmptyError(DocumentDateValidationError, IncorrectData):
    description = 'for fns only empty allowed'
    description_ru = 'для платежей в ФНС значение должно быть пустым'


class DocumentDateValidationCustomsLenError(DocumentDateValidationError, ExactFieldLenError):
    description = 'for customs value must be equal 10 chars'
    description_ru = 'для платежей в таможню длина значения должна быть 10 символов'
    required_len = 10


class DocumentDateValidationBOLenError(DocumentDateValidationError, IncorrectLen):
    description = 'for bo value max 10 chars'
    description_ru = 'для иных платежей в бюджет значение не должно быть длиннее 10 символов'


class DocumentDateValidationCustomsReasonValueError(DocumentDateValidationError, IncorrectData):
    description = 'for customs with reason = "00" value have to be "0" or "00" or empty'
    description_ru = 'для платежей в таможню c основанием платежа "00" значение должно быть пустым или "0" или "00"'


class BudgetPaymentForThirdPersonError(VityaDescribedError, PydanticValueError):
    target = None
    target_ru = None
    description = 'budget payment can not for third person'
    description_ru = 'платеж в бюджет не может быть за третье лицо'


class TypeOfIncomeValidationError(VityaDescribedError, PydanticValueError):
    target = 'type of income'
    target_ru = 'Код вида дохода'
    description = 'type of income can be only in 1, 2, 3, 4, 5'
    description_ru = 'код вида дохода может быть только 1, 2, 3, 4, 5'


class TypeOfIncomeValidationTypeError(TypeOfIncomeValidationError):
    description = 'must be str'
    description_ru = 'должен быть строкой'


class ReceiverAccountValidationBudgetPayerStatusError(ReceiverAccountValidationError, IncorrectData):
    description = (
        'for budget payment with payer status in 01, 02, 04, 06, 07, 13, 16, 17, 28, 30 '
        'account must start with "03100"'
    )
    description_ru = (
        'для платежей в бюджет со статусом плательщика 01, 02, 04, 06, 07, 13, 16, 17, '
        '28, 30 счет должен начинаться с "03100"'
    )


class ReceiverAccountValidationBudgetOtherPayerStatusError(ReceiverAccountValidationError, IncorrectData):
    description = (
        'for budget other payment with payer status = 31 account must start with "03212"'
    )
    description_ru = (
        'для иных платежей в бюджет со статусом плательщика 31 счет должен начинаться с "03212"'
    )


class TaxPeriodValidationBOValueOnlyOneZeroAllowed(TaxPeriodValidationError, IncorrectData):
    description = 'for bo must contain only one "0"'
    description_ru = 'для иных платежей в бюджет значение не должно состоять из более чем одного "0"'
