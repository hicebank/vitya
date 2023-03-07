from enum import Enum


class PaymentType(str, Enum):
    fns = 'fns'  # бюджетный платеж в ФНС
    tms = 'tms'  # бюджетный платеж в таможню
    bo = 'bo'  # бюджетный платеж иное
    ip = 'ip'  # платеж на ИП
    fl = 'fl'  # платеж на ФЛ
    le = 'le'  # платеж на ЮР

    @classmethod
    def budget_types(cls) -> list['PaymentType']:
        return [PaymentType.fns, PaymentType.tms, PaymentType.bo]

    @property
    def is_budget(self) -> bool:
        return self in self.budget_types()
