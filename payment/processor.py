# payment/processor.py
# ----------------------------------------------------------------------
# PaymentProcessor: Core payment module with strict input validation.
# This is the FIXED version — the original bug was that process_payment()
# had no null check on `amount`, causing a TypeError when None was passed.
# ----------------------------------------------------------------------

from decimal import Decimal, InvalidOperation
from payment.exceptions import PaymentValidationError, PaymentProcessingError

SUPPORTED_CURRENCIES = {"INR", "USD", "EUR", "GBP"}
PROCESSING_FEE_RATE  = Decimal("0.02")   # 2% processing fee


class PaymentProcessor:
    """Handles payment validation and processing with strict input guards."""

    def __init__(self, gateway_id: str = "default-gateway"):
        self.gateway_id  = gateway_id
        self.transaction_log = []

    def process_payment(self, amount, currency: str = "INR") -> dict:
        """
        Validates and processes a payment transaction.

        Args:
            amount:   The payment amount. Must be a positive number.
            currency: ISO 4217 currency code. Must be in SUPPORTED_CURRENCIES.

        Returns:
            dict with status, total, currency, and transaction_id.

        Raises:
            PaymentValidationError: If amount or currency is invalid.
        """

        # ── Fix applied: guard clause for None amount ─────────────────
        # Original bug: this check was missing entirely, causing TypeError
        # when amount * PROCESSING_FEE_RATE was attempted with None.
        if amount is None:
            raise PaymentValidationError(
                field="amount",
                reason="Amount cannot be None. A numeric value is required."
            )

        # ── Type validation ───────────────────────────────────────────
        try:
            amount_decimal = Decimal(str(amount))
        except (InvalidOperation, TypeError):
            raise PaymentValidationError(
                field="amount",
                reason=f"Amount must be numeric, got: {type(amount).__name__}"
            )

        # ── Range validation ──────────────────────────────────────────
        if amount_decimal <= 0:
            raise PaymentValidationError(
                field="amount",
                reason=f"Amount must be greater than zero, got: {amount_decimal}"
            )

        # ── Currency validation ───────────────────────────────────────
        if currency not in SUPPORTED_CURRENCIES:
            raise PaymentValidationError(
                field="currency",
                reason=f"'{currency}' is not supported. Use: {SUPPORTED_CURRENCIES}"
            )

        # ── Process ───────────────────────────────────────────────────
        fee   = amount_decimal * PROCESSING_FEE_RATE
        total = amount_decimal + fee

        transaction_id = f"TXN-{self.gateway_id}-{len(self.transaction_log) + 1:04d}"

        record = {
            "status":         "success",
            "transaction_id": transaction_id,
            "original":       float(amount_decimal),
            "fee":            float(fee),
            "total":          float(total),
            "currency":       currency,
        }

        self.transaction_log.append(record)
        return record

    def get_transaction_count(self) -> int:
        """Returns the number of transactions processed in this session."""
        return len(self.transaction_log)