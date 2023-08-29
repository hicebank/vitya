from typing import Any, Optional


class VityaDescribedError(Exception):
    target: Optional[str]
    description: str

    target_ru: Optional[str]
    description_ru: str

    def __str__(self) -> str:
        if self.target:
            return f'invalid {self.target}: {self.description}'
        return f'{self.description}'

    def __getattr__(self, item: str) -> Any:
        if item.endswith('_ru'):
            return getattr(self, item[:-3])
        raise AttributeError


class NeedRequiredField(VityaDescribedError):
    pass


class IncorrectLen(VityaDescribedError):
    pass


class ExactFieldLenError(VityaDescribedError):
    required_len: int


class IncorrectData(VityaDescribedError):
    pass
