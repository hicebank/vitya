from itertools import chain
from typing import List, Sequence, TypedDict

import pydantic
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from pydantic.errors import NoneIsNotAllowedError, MissingError
from vitya.errors_base import NeedRequiredField, IncorrectLen, ExactFieldLenError, IncorrectData
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


class AlertGenerator:
    _key_to_ru = {
        'amount': 'Сумма',
        'payer': 'Плательщик',
        'receiver_bic': 'БИК банка получателя',
        'receiver': 'Получатель',
        'receiver_account_number': 'Номер счёта получателя',
    }

    def __init__(self, key_to_field_name: AlertKeyToFieldName):
        self._field_name_to_key = {value: key for key, value in key_to_field_name.items()}

    def get_error_client_alerts(self, exc: Exception) -> List[str]:
        if not isinstance(exc, ValidationError):
            return []

        result = []
        for error_wrapper in flatten_error_wrappers(exc.raw_errors):
            if isinstance(error_wrapper.exc, CheckerError):
                for exc in error_wrapper.exc.errors:
                    if isinstance(exc, NeedRequiredField):
                        result.append(f'Поле «{exc.target_ru}» должно быть заполнено')
                    elif isinstance(exc, IncorrectLen):
                        result.append(f'Поле «{exc.target_ru}» содержит неправильное количество символов')
                    elif isinstance(exc, ExactFieldLenError):
                        result.append(f'Поле «{exc.target_ru}» должно содержать ровно {exc.required_len} символов')
                    elif isinstance(exc, IncorrectData):
                        result.append(f'Поле «{exc.target_ru}» содержит некорректные данные')
                    elif isinstance(exc, DocumentNumberValidationBOEmptyNotAllowed):
                        result.append(
                            'При выборе «24» в поле «101, Статус плательщика» обязательны данные'
                            ' хотя бы одного из полей: «60, ИНН плательщика», «22, УИН», «108, Документ»'
                        )
            elif isinstance(error_wrapper.exc, (NoneIsNotAllowedError, MissingError)):
                if len(error_wrapper.loc_tuple()) == 1:
                    field_name = error_wrapper.loc_tuple()[0]
                    if field_name in self._field_name_to_key:
                        name_ru = self._key_to_ru[self._field_name_to_key[field_name]]
                        result.append(f'Поле «{name_ru}» должно быть заполнено')
        return result
