from itertools import chain
from typing import List, Optional, Sequence, TypedDict

import pydantic
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from pydantic.errors import MissingError, NoneIsNotAllowedError

from vitya.errors_base import (
    ExactFieldLenError,
    IncorrectData,
    IncorrectLen,
    NeedRequiredField,
)
from vitya.payment_order.errors import DocumentNumberValidationBOEmptyNotAllowed
from vitya.payment_order.payments.checkers import CheckerError


def flatten_error_wrappers(error_list: pydantic.error_wrappers.ErrorList) -> List[ErrorWrapper]:
    if isinstance(error_list, Sequence):
        return list(chain.from_iterable(map(flatten_error_wrappers, error_list)))
    return [error_list]


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
    failed_field: str
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
                    failed_field=exc.target,  # type: ignore
                    failed_field_class_name=None
                )]
            return [AlertBody(
                alert=None,
                failed_field=getattr(exc, 'target', None),
                failed_field_class_name=None
            )]

        result = []
        for error_wrapper in flatten_error_wrappers(exc.raw_errors):
            if isinstance(error_wrapper.exc, CheckerError):
                for sub_error in error_wrapper.exc.errors:
                    alert = self._mixin_to_alert(sub_error)
                    if alert is not None:
                        result.append(AlertBody(
                            alert=alert,
                            failed_field=sub_error.target,  # type: ignore
                            failed_field_class_name=self._format_failed_field_class_name(
                                error_wrapper.loc_tuple()[0]  # type: ignore
                            )
                        ))
            elif isinstance(error_wrapper.exc, (NoneIsNotAllowedError, MissingError)):
                if len(error_wrapper.loc_tuple()) == 1:
                    field_name = error_wrapper.loc_tuple()[0]
                    if field_name in self._field_name_to_key:
                        target_ru = self._key_to_ru[self._field_name_to_key[field_name]]
                        result.append(AlertBody(
                            alert=f'Поле «{target_ru}» должно быть заполнено',
                            failed_field=self._field_name_to_key[field_name],
                            failed_field_class_name=self._format_failed_field_class_name(field_name)  # type: ignore
                        ))
            else:
                alert = self._mixin_to_alert(error_wrapper.exc)
                if alert is not None:
                    result.append(AlertBody(
                        alert=alert,
                        failed_field=error_wrapper.exc.target,  # type: ignore
                        failed_field_class_name=self._format_failed_field_class_name(
                            error_wrapper.loc_tuple()[0]  # type: ignore
                        )
                    ))
                else:
                    result.append(AlertBody(
                        alert=None,
                        failed_field=error_wrapper.exc.target,  # type: ignore
                        failed_field_class_name=self._format_failed_field_class_name(
                            error_wrapper.loc_tuple()[0]  # type: ignore
                        )
                    ))
        return result
