from vitya.payment_order.enums import AccountKind
from vitya.payment_order.fields import AccountNumber

IP_ACCOUNTS_PREFIXES_5 = {
    '40802', '45914', '47610', '47611', '47832',
    *[str(prefix) for prefix in range(42108, 42114 + 1)]
}
FL_ACCOUNTS_PREFIXES_5 = {
    '40803', '40810', '40813', '40817', '40820', '40824', '40826', '40827', '40828', '40914', '45815',
    '45817', '45915', '45917', '47411', '47468', '47603', '47605', '47608', '47609', '47833', '47835',
}
FL_ACCOUNTS_PREFIXES_3 = {
    '423', '426', '455', '457',
}
CHAMELEON_PREFIXES_3 = {
    '454',
}
CHAMELEON_PREFIXES_5 = {
    '40804', '40805', '40915', '40806', '40809', '40812',
    '40814', '40815', '40827', '40828', '40830', '40831', '40911',
    '45814',
}

PREFIX_5_TO_ACCOUNT_KIND = {
    **{prefix: AccountKind.IP for prefix in IP_ACCOUNTS_PREFIXES_5},
    **{prefix: AccountKind.FL for prefix in FL_ACCOUNTS_PREFIXES_5},
    **{prefix: AccountKind.CHAMELEON for prefix in CHAMELEON_PREFIXES_5},
}
PREFIX_3_TO_ACCOUNT_KIND = {
    **{prefix: AccountKind.FL for prefix in FL_ACCOUNTS_PREFIXES_3},
    **{prefix: AccountKind.CHAMELEON for prefix in CHAMELEON_PREFIXES_3},
}


def get_account_kind(account_number: AccountNumber) -> AccountKind:
    try:
        return PREFIX_5_TO_ACCOUNT_KIND[account_number[:5]]
    except KeyError:
        return PREFIX_3_TO_ACCOUNT_KIND.get(account_number[:3], AccountKind.LE)
