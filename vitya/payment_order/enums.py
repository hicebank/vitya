from enum import Enum
from typing import List


class AccountKind(str, Enum):
    IP = 'ip'                           # счет ИП
    FL = 'fl'                           # счет ФЛ
    LE = 'le'                           # счет ЮР
    CHAMELEON = 'chameleon'             # счет Хамелеона


class PaymentType(str, Enum):
    FNS = 'fns'                         # бюджетный платеж в ФНС
    CUSTOMS = 'customs'                 # бюджетный платеж в таможню
    BUDGET_OTHER = 'budget_other'       # бюджетный платеж иное
    IP = 'ip'                           # платеж на ИП
    FL = 'fl'                           # платеж на ФЛ
    LE = 'le'                           # платеж на ЮР
    CHAMELEON = 'chameleon'             # платеж на Хамелеона

    @classmethod
    def budget_types(cls) -> List['PaymentType']:
        return [PaymentType.FNS, PaymentType.CUSTOMS, PaymentType.BUDGET_OTHER]

    @property
    def is_budget(self) -> bool:
        return self in self.budget_types()

    @property
    def name_ru(self) -> str:
        return _PAYMENT_TYPE_TO_RU[self]


_PAYMENT_TYPE_TO_RU = {
    PaymentType.FNS: 'ФНС',
    PaymentType.CUSTOMS: 'Таможня',
    PaymentType.BUDGET_OTHER: 'Иные',
    PaymentType.IP: 'ИП',
    PaymentType.FL: 'ФЛ',
    PaymentType.LE: 'ЮЛ',
    PaymentType.CHAMELEON: 'Хамелеон',
}
