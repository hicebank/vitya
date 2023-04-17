class VityaDescribedError(Exception):
    target: str
    description: str

    target_ru: str
    description_ru: str

    def __str__(self):
        return f"invalid {self.target}: {self.description}"

    def __getattr__(self, item: str):
        if item.endswith('_ru'):
            return getattr(self, item[:-3])
        raise AttributeError
