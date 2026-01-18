"""Tests for input validation security fixes."""

import pytest
from main import validate_inputs, MIN_CAPITAL, MAX_CAPITAL


class TestValidateInputsTicker:
    """Tests for ticker validation."""

    def test_valid_ticker_uppercase(self):
        """Valid uppercase ticker should pass."""
        validate_inputs('TSLA', '2024-01-01', '2024-12-31', 50000)

    def test_valid_ticker_lowercase(self):
        """Valid lowercase ticker should pass."""
        validate_inputs('aapl', '2024-01-01', '2024-12-31', 50000)

    def test_valid_ticker_mixed_case(self):
        """Valid mixed case ticker should pass."""
        validate_inputs('TsLa', '2024-01-01', '2024-12-31', 50000)

    def test_valid_ticker_single_char(self):
        """Single character ticker should pass."""
        validate_inputs('A', '2024-01-01', '2024-12-31', 50000)

    def test_valid_ticker_five_chars(self):
        """Five character ticker should pass."""
        validate_inputs('GOOGL', '2024-01-01', '2024-12-31', 50000)

    def test_invalid_ticker_too_long(self):
        """Ticker longer than 5 chars should fail."""
        with pytest.raises(ValueError, match="Invalid ticker"):
            validate_inputs('TOOLONG', '2024-01-01', '2024-12-31', 50000)

    def test_invalid_ticker_empty(self):
        """Empty ticker should fail."""
        with pytest.raises(ValueError, match="Invalid ticker"):
            validate_inputs('', '2024-01-01', '2024-12-31', 50000)

    def test_invalid_ticker_with_numbers(self):
        """Ticker with numbers should fail."""
        with pytest.raises(ValueError, match="Invalid ticker"):
            validate_inputs('TSL4', '2024-01-01', '2024-12-31', 50000)

    def test_invalid_ticker_with_special_chars(self):
        """Ticker with special characters should fail."""
        with pytest.raises(ValueError, match="Invalid ticker"):
            validate_inputs('TS-LA', '2024-01-01', '2024-12-31', 50000)

    def test_invalid_ticker_with_spaces(self):
        """Ticker with spaces should fail."""
        with pytest.raises(ValueError, match="Invalid ticker"):
            validate_inputs('TS LA', '2024-01-01', '2024-12-31', 50000)

    def test_invalid_ticker_sql_injection(self):
        """SQL injection attempt should fail."""
        with pytest.raises(ValueError, match="Invalid ticker"):
            validate_inputs("'; DROP TABLE", '2024-01-01', '2024-12-31', 50000)

    def test_invalid_ticker_path_traversal(self):
        """Path traversal attempt should fail."""
        with pytest.raises(ValueError, match="Invalid ticker"):
            validate_inputs('../etc', '2024-01-01', '2024-12-31', 50000)


class TestValidateInputsCapital:
    """Tests for capital validation."""

    def test_valid_capital_minimum(self):
        """Minimum capital should pass."""
        validate_inputs('TSLA', '2024-01-01', '2024-12-31', MIN_CAPITAL)

    def test_valid_capital_maximum(self):
        """Maximum capital should pass."""
        validate_inputs('TSLA', '2024-01-01', '2024-12-31', MAX_CAPITAL)

    def test_valid_capital_typical(self):
        """Typical capital amount should pass."""
        validate_inputs('TSLA', '2024-01-01', '2024-12-31', 50000)

    def test_invalid_capital_below_minimum(self):
        """Capital below minimum should fail."""
        with pytest.raises(ValueError, match="Capital must be between"):
            validate_inputs('TSLA', '2024-01-01', '2024-12-31', MIN_CAPITAL - 1)

    def test_invalid_capital_above_maximum(self):
        """Capital above maximum should fail."""
        with pytest.raises(ValueError, match="Capital must be between"):
            validate_inputs('TSLA', '2024-01-01', '2024-12-31', MAX_CAPITAL + 1)

    def test_invalid_capital_zero(self):
        """Zero capital should fail."""
        with pytest.raises(ValueError, match="Capital must be between"):
            validate_inputs('TSLA', '2024-01-01', '2024-12-31', 0)

    def test_invalid_capital_negative(self):
        """Negative capital should fail."""
        with pytest.raises(ValueError, match="Capital must be between"):
            validate_inputs('TSLA', '2024-01-01', '2024-12-31', -10000)


class TestValidateInputsDates:
    """Tests for date validation."""

    def test_valid_dates(self):
        """Valid date range should pass."""
        validate_inputs('TSLA', '2024-01-01', '2024-12-31', 50000)

    def test_valid_dates_same_month(self):
        """Dates in same month should pass."""
        validate_inputs('TSLA', '2024-01-01', '2024-01-31', 50000)

    def test_valid_dates_multi_year(self):
        """Multi-year date range should pass."""
        validate_inputs('TSLA', '2022-01-01', '2024-12-31', 50000)

    def test_invalid_start_date_format(self):
        """Invalid start date format should fail."""
        with pytest.raises(ValueError, match="Invalid start date"):
            validate_inputs('TSLA', '01-01-2024', '2024-12-31', 50000)

    def test_invalid_end_date_format(self):
        """Invalid end date format should fail."""
        with pytest.raises(ValueError, match="Invalid end date"):
            validate_inputs('TSLA', '2024-01-01', '12-31-2024', 50000)

    def test_invalid_start_date_garbage(self):
        """Garbage start date should fail."""
        with pytest.raises(ValueError, match="Invalid start date"):
            validate_inputs('TSLA', 'not-a-date', '2024-12-31', 50000)

    def test_invalid_end_date_garbage(self):
        """Garbage end date should fail."""
        with pytest.raises(ValueError, match="Invalid end date"):
            validate_inputs('TSLA', '2024-01-01', 'not-a-date', 50000)

    def test_invalid_dates_same_day(self):
        """Same start and end date should fail."""
        with pytest.raises(ValueError, match="must be before"):
            validate_inputs('TSLA', '2024-01-01', '2024-01-01', 50000)

    def test_invalid_dates_reversed(self):
        """End date before start date should fail."""
        with pytest.raises(ValueError, match="must be before"):
            validate_inputs('TSLA', '2024-12-31', '2024-01-01', 50000)

    def test_invalid_start_date_nonexistent(self):
        """Non-existent start date should fail."""
        with pytest.raises(ValueError, match="Invalid start date"):
            validate_inputs('TSLA', '2024-02-30', '2024-12-31', 50000)

    def test_invalid_end_date_nonexistent(self):
        """Non-existent end date should fail."""
        with pytest.raises(ValueError, match="Invalid end date"):
            validate_inputs('TSLA', '2024-01-01', '2024-13-01', 50000)
