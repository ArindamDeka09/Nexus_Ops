# payment/exceptions.py
# ----------------------------------------------------------------------
# Custom exceptions for the payment processing domain.
# Separating exception types lets callers handle validation errors
# differently from runtime processing errors.
# ----------------------------------------------------------------------


class PaymentValidationError(ValueError):
    """
    Raised when the payment payload fails input validation.
    Examples: amount is None, negative, or wrong type.
    """
    def __init__(self, field: str, reason: str):
        self.field  = field
        self.reason = reason
        super().__init__(f"Validation failed for '{field}': {reason}")


class PaymentProcessingError(RuntimeError):
    """
    Raised when a structurally valid payment fails during processing.
    Examples: gateway timeout, currency not supported.
    """
    def __init__(self, message: str):
        super().__init__(f"Payment processing error: {message}")