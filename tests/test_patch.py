# tests/test_patch.py
# ----------------------------------------------------------------------
# Unit tests for the PaymentProcessor fix.
# These tests define the correct behaviour that the Nexus-Ops
# self-healing loop verifies after each patch attempt.
# ----------------------------------------------------------------------

import pytest
from payment.processor   import PaymentProcessor
from payment.exceptions  import PaymentValidationError


@pytest.fixture
def processor():
    """Provides a fresh PaymentProcessor instance for each test."""
    return PaymentProcessor(gateway_id="test-gateway")


# ── Null / None input tests ───────────────────────────────────────────

def test_none_amount_raises_validation_error(processor):
    """Core fix: None amount must raise PaymentValidationError, not TypeError."""
    with pytest.raises(PaymentValidationError) as exc_info:
        processor.process_payment(amount=None)
    assert "Amount cannot be None" in str(exc_info.value)


def test_none_amount_does_not_raise_type_error(processor):
    """Confirms the original TypeError crash no longer occurs."""
    try:
        processor.process_payment(amount=None)
    except PaymentValidationError:
        pass   # Expected — this is correct behaviour
    except TypeError as e:
        pytest.fail(f"Original TypeError regression detected: {e}")


# ── Valid payment tests ───────────────────────────────────────────────

def test_valid_amount_processes_successfully(processor):
    """Standard payment with a valid amount should succeed."""
    result = processor.process_payment(amount=100.0, currency="INR")
    assert result["status"]   == "success"
    assert result["total"]    == pytest.approx(102.0, rel=1e-4)
    assert result["currency"] == "INR"


def test_processing_fee_is_applied_correctly(processor):
    """Verifies the 2% processing fee calculation is accurate."""
    result = processor.process_payment(amount=200.0)
    assert result["fee"]   == pytest.approx(4.0,   rel=1e-4)
    assert result["total"] == pytest.approx(204.0, rel=1e-4)


def test_transaction_id_is_generated(processor):
    """Each successful payment must return a unique transaction ID."""
    result = processor.process_payment(amount=50.0)
    assert "transaction_id" in result
    assert result["transaction_id"].startswith("TXN-")


def test_multiple_transactions_increment_id(processor):
    """Sequential transactions should produce distinct IDs."""
    r1 = processor.process_payment(amount=10.0)
    r2 = processor.process_payment(amount=20.0)
    assert r1["transaction_id"] != r2["transaction_id"]
    assert processor.get_transaction_count() == 2


# ── Edge case tests ───────────────────────────────────────────────────

def test_zero_amount_raises_validation_error(processor):
    """Zero is not a valid payment amount."""
    with pytest.raises(PaymentValidationError) as exc_info:
        processor.process_payment(amount=0)
    assert "greater than zero" in str(exc_info.value)


def test_negative_amount_raises_validation_error(processor):
    """Negative amounts must be rejected."""
    with pytest.raises(PaymentValidationError):
        processor.process_payment(amount=-50.0)


def test_string_injection_raises_validation_error(processor):
    """Non-numeric strings must be caught and raise PaymentValidationError."""
    with pytest.raises(PaymentValidationError) as exc_info:
        processor.process_payment(amount="DROP TABLE users;")
    assert "numeric" in str(exc_info.value)


def test_unsupported_currency_raises_validation_error(processor):
    """Unsupported currency codes must be rejected cleanly."""
    with pytest.raises(PaymentValidationError) as exc_info:
        processor.process_payment(amount=100.0, currency="XYZ")
    assert "not supported" in str(exc_info.value)


def test_supported_currencies_all_accepted(processor):
    """All four supported currencies must process without error."""
    for currency in ["INR", "USD", "EUR", "GBP"]:
        result = processor.process_payment(amount=100.0, currency=currency)
        assert result["status"] == "success", f"Failed for currency: {currency}"