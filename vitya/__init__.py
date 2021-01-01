import re
from typing import List


def validate_inn(inn: str) -> None:
    """
    TODO
    """
    if not inn:
        raise ValueError("inn is empty")
    elif not re.fullmatch(r'[0-9]+', inn):
        raise ValueError("inn can contain only numbers")
    elif len(inn) not in [10, 12]:
        raise ValueError("inn can consists only 10 or 12 numbers")

    def check_digits(inn: str, coefficients: List[int]) -> int:
        n = 0
        for idx, coefficient in enumerate(coefficients):
            n += coefficient * int(inn[idx])
        return n % 11 % 10

    if len(inn) == 10:
        n10 = check_digits(inn, [2, 4, 10, 3, 5, 9, 4, 6, 8])
        if n10 != int(inn[9]):
            raise ValueError("wrong checksum")
        return

    if len(inn) == 12:
        n11 = check_digits(inn, [7, 2, 4, 10, 3, 5, 9, 4, 6, 8])
        n12 = check_digits(inn, [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8])
        if n11 == int(inn[10]) and n12 == int(inn[11]):
            raise ValueError("wrong checksum")
        return

    raise ValueError("wrong size of inn")
