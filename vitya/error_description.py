from typing import Any, Iterator, List, Optional, Sequence, Tuple, TypedDict

from pydantic import ValidationError

from vitya._pydantic import PYDANTIC_V2
from vitya.errors_base import (
    ExactFieldLenError,
    IncorrectData,
    IncorrectLen,
    NeedRequiredField,
)
from vitya.payment_order.errors import (
    DocumentNumberValidationBOEmptyNotAllowed,
    ReceiverAccountValidationBICValueError,
)
from vitya.payment_order.payments.checkers import CheckerError

if not PYDANTIC_V2:
    from itertools import chain

    from pydantic.error_wrappers import ErrorList, ErrorWrapper
    from pydantic.errors import MissingError, NoneIsNotAllowedError

    def flatten_error_wrappers(error_list: ErrorList) -> List[ErrorWrapper]:
        if isinstance(error_list, Sequence):
            return list(chain.from_iterable(map(flatten_error_wrappers, error_list)))
        return [error_list]


def _validation_issues(exc: ValidationError) -> Iterator[Tuple[Tuple[Any, ...], Optional[Exception], bool]]:
    if PYDANTIC_V2:
        for detail in exc.errors(include_url=False):
            cause = detail.get('ctx', {}).get('error')
            missing = detail['type'] in ('missing', 'vitya_empty') or (cause is None and detail.get('input') is None)
            yield detail['loc'], cause, missing
    else:
        for wrapper in flatten_error_wrappers(exc.raw_errors):
            yield wrapper.loc_tuple(), wrapper.exc, isinstance(wrapper.exc, (NoneIsNotAllowedError, MissingError))


class AlertKeyToFieldName(TypedDict):
    amount: str
    payer: str
    payer_bic: str
    payer_account_number: str
    receiver_bic: str
    receiver: str
    receiver_account_number: str
    receiver_inn: str
    receiver_kpp: str
    receiver_bank_name: str
    receiver_bank_cs: str
    tax_payer_status: str


class AlertBody(TypedDict):
    alert: Optional[str]
    failed_field: Optional[str]
    failed_field_class_name: Optional[str]


class AlertGenerator:
    _key_to_ru = {
        'amount': 'Сумма',
        'payer': 'Плательщик',
        'receiver_bic': 'БИК банка получателя',
        'receiver': 'Получатель',
        'receiver_account_number': 'Номер счёта получателя',
        'payer_account_number': 'Номер счёта плательщика',
        'payer_bic': 'БИК банка плательщика',
        'receiver_inn': 'ИНН получателя',
        'receiver_kpp': 'КПП получателя',
        'receiver_bank_name': 'Наименование банка получателя',
        'receiver_bank_cs': 'Кор счет банка получателя',
        'tax_payer_status': 'Статус плательщика',
    }

    def __init__(self, key_to_field_name: AlertKeyToFieldName):
        self._field_name_to_key = {value: key for key, value in key_to_field_name.items()}

    def _mixin_to_alert(self, exc: Exception) -> Optional[str]:
        if isinstance(exc, NeedRequiredField):
            return f'Поле «{exc.target_ru}» должно быть заполнено'
        if isinstance(exc, IncorrectLen):
            return f'Поле «{exc.target_ru}» содержит неправильное количество символов'
        if isinstance(exc, ExactFieldLenError):
            return f'Поле «{exc.target_ru}» должно содержать ровно {exc.required_len} символов'
        if isinstance(exc, ReceiverAccountValidationBICValueError):
            return 'Такого счета нет в банке'
        if isinstance(exc, IncorrectData):
            return f'Поле «{exc.target_ru}» содержит некорректные данные'
        if isinstance(exc, DocumentNumberValidationBOEmptyNotAllowed):
            return (
                'При выборе «24» в поле «101, Статус плательщика» обязательны данные'
                ' хотя бы одного из полей: «60, ИНН плательщика», «22, УИН», «108, Документ»'
            )
        return None

    def _format_failed_field_class_name(self, failed_field_class_name: str) -> Optional[str]:
        if failed_field_class_name == '__root__':
            return None
        return failed_field_class_name

    def get_error_client_alerts(self, exc: Exception) -> List[AlertBody]:
        if not isinstance(exc, ValidationError):
            alert = self._mixin_to_alert(exc)
            if alert is not None:
                return [AlertBody(
                    alert=alert,
                    failed_field=getattr(exc, 'target', None),
                    failed_field_class_name=None
                )]
            return [AlertBody(
                alert=None,
                failed_field=getattr(exc, 'target', None),
                failed_field_class_name=None
            )]

        result = []
        for loc, cause, missing in _validation_issues(exc):
            field_name = loc[0] if loc else '__root__'
            class_name = self._format_failed_field_class_name(field_name)
            if missing:
                if len(loc) == 1 and field_name in self._field_name_to_key:
                    key = self._field_name_to_key[field_name]
                    result.append(AlertBody(
                        alert=f'Поле «{self._key_to_ru[key]}» должно быть заполнено',
                        failed_field=key,
                        failed_field_class_name=class_name,
                    ))
            elif isinstance(cause, CheckerError):
                for sub_error in cause.errors:
                    alert = self._mixin_to_alert(sub_error)
                    if alert is not None:
                        result.append(AlertBody(
                            alert=alert,
                            failed_field=getattr(sub_error, 'target', None),
                            failed_field_class_name=class_name,
                        ))
            else:
                result.append(AlertBody(
                    alert=self._mixin_to_alert(cause) if cause is not None else None,
                    failed_field=getattr(cause, 'target', None),
                    failed_field_class_name=class_name,
                ))
        return result
