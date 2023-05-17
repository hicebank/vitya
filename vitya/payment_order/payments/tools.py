from vitya.payment_order.enums import AccountKind
from vitya.payment_order.fields import AccountNumber

IP_ACCOUNTS_PREFIXES = {'40802', *[str(prefix) for prefix in range(42018, 42113 + 1)]}
FL_ACCOUNTS_PREFIXES = ('40817', '40820', '40911', '423', '426')


def get_account_kind(account_number: AccountNumber) -> AccountKind:
    if account_number[:5] in IP_ACCOUNTS_PREFIXES:
        return AccountKind.IP
    if account_number.startswith(FL_ACCOUNTS_PREFIXES):
        return AccountKind.FL
    return AccountKind.LE
