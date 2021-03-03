class ValidationError(ValueError):
    """
    Exception that raises if passed data is invalid
    """
    pass


class InnValidationError(ValidationError):
    pass


class OgrnValidationError(ValidationError):
    pass


class KppValidationError(ValidationError):
    pass


class BicValidationError(ValidationError):
    pass


class SnilsValidationError(ValidationError):
    pass

