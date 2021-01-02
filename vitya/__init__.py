import re
from typing import List


class ValidationError(ValueError):
    """
    Exception that raises if passed data is invalid
    """
    pass


def validate_inn(inn: str) -> None:
    """
    Source:
    https://www.consultant.ru/document/cons_doc_LAW_134082/947eeb5630c9f58cbc6103f0910440cef8eaccac/
    https://ru.wikipedia.org/wiki/%D0%98%D0%B4%D0%B5%D0%BD%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%86%D0%B8%D0%BE%D0%BD%D0%BD%D1%8B%D0%B9_%D0%BD%D0%BE%D0%BC%D0%B5%D1%80_%D0%BD%D0%B0%D0%BB%D0%BE%D0%B3%D0%BE%D0%BF%D0%BB%D0%B0%D1%82%D0%B5%D0%BB%D1%8C%D1%89%D0%B8%D0%BA%D0%B0
    """
    if not inn:
        raise ValidationError("inn is empty")

    if not isinstance(inn, str):
        raise ValidationError("inn should be passed as string")

    if not re.fullmatch(r'[0-9]+', inn):
        raise ValidationError("inn can contain only numbers")

    def count_checksum(inn: str, coefficients: List[int]) -> int:
        assert len(inn) >= len(coefficients)
        n = sum([int(a) * b for a, b in zip(inn[:len(coefficients)], coefficients)])
        return n % 11 % 10

    if len(inn) == 10:
        n10 = count_checksum(inn, [2, 4, 10, 3, 5, 9, 4, 6, 8])
        if n10 != int(inn[9]):
            raise ValidationError(f"wrong checksum on last digit: {inn[9]}; expected: {n10}")
        return

    if len(inn) == 12:
        n11 = count_checksum(inn, [7, 2, 4, 10, 3, 5, 9, 4, 6, 8])
        if n11 != int(inn[10]):
            raise ValidationError(f"wrong checksum on pre-last digit: {inn[10]}; expected: {n11}")

        n12 = count_checksum(inn, [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8])
        if n12 != int(inn[11]):
            raise ValidationError(f"wrong checksum on last digit: {inn[11]}; expected: {n12}")
        return

    raise ValidationError("wrong size of inn, it can be 10 or 12 only")
