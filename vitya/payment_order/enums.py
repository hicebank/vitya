from enum import Enum
from typing import List


class PaymentType(str, Enum):
    FNS = 'fns'                         # бюджетный платеж в ФНС
    CUSTOMS = 'customs'                 # бюджетный платеж в таможню
    BUDGET_OTHER = 'budget_other'       # бюджетный платеж иное
    IP = 'ip'                           # платеж на ИП
    FL = 'fl'                           # платеж на ФЛ
    LE = 'le'                           # платеж на ЮР

    @classmethod
    def budget_types(cls) -> List['PaymentType']:
        return [PaymentType.FNS, PaymentType.CUSTOMS, PaymentType.BUDGET_OTHER]

    @property
    def is_budget(self) -> bool:
        return self in self.budget_types()
