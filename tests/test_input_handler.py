"""Tests for input_handler.py - STEP 2 user input validation."""

import pytest

from src.input_handler import (
    UserInput,
    get_validated_input,
    parse_price,
    validate_city,
    validate_price,
)


class TestValidateCity:
    """Tests for validate_city."""

    def test_empty_city_invalid(self):
        """Empty or whitespace city is invalid."""
        assert validate_city("") == (False, "City cannot be empty.")
        assert validate_city("   ") == (False, "City cannot be empty.")

    def test_non_empty_city_valid_without_allowed_list(self):
        """Non-empty city is valid when allowed_cities not provided."""
        assert validate_city("Banashankari") == (True, "")
        assert validate_city("Bangalore") == (True, "")

    def test_city_in_allowed_list_valid(self):
        """City in allowed list (case-insensitive) is valid."""
        allowed = ["Banashankari", "Bangalore", "Koramangala"]
        assert validate_city("Banashankari", allowed_cities=allowed) == (True, "")
        assert validate_city("banashankari", allowed_cities=allowed) == (True, "")
        assert validate_city(" BANGALORE ", allowed_cities=allowed) == (True, "")

    def test_city_not_in_allowed_list_invalid(self):
        """City not in allowed list is invalid when list provided."""
        allowed = ["Banashankari", "Bangalore"]
        valid, msg = validate_city("Mumbai", allowed_cities=allowed)
        assert valid is False
        assert "Mumbai" in msg or "not found" in msg.lower()


class TestParsePrice:
    """Tests for parse_price."""

    @pytest.mark.parametrize("value,expected", [("800", 800.0), ("600", 600.0), ("1000", 1000.0)])
    def test_valid_strings(self, value, expected):
        assert parse_price(value) == expected

    def test_with_comma(self):
        assert parse_price("1,000") == 1000.0

    @pytest.mark.parametrize("value", ["", "  ", None, "abc", "12.34.56"])
    def test_invalid_returns_none(self, value):
        assert parse_price(value) is None


class TestValidatePrice:
    """Tests for validate_price."""

    def test_no_price_invalid(self):
        """Missing price is invalid."""
        valid, msg = validate_price()
        assert valid is False
        assert "required" in msg.lower() or "Price" in msg

    def test_valid_single_price(self):
        assert validate_price(price=800) == (True, "")
        assert validate_price(max_price=600) == (True, "")

    def test_negative_price_invalid(self):
        valid, msg = validate_price(price=-100)
        assert valid is False
        assert "positive" in msg.lower()

    def test_zero_price_invalid(self):
        valid, msg = validate_price(price=0)
        assert valid is False

    def test_valid_range(self):
        assert validate_price(min_price=300, max_price=800) == (True, "")

    def test_min_greater_than_max_invalid(self):
        valid, msg = validate_price(min_price=1000, max_price=500)
        assert valid is False
        assert "greater" in msg.lower() or "max" in msg.lower()


class TestGetValidatedInput:
    """Tests for get_validated_input."""

    def test_returns_user_input(self):
        u = get_validated_input("Banashankari", price=600)
        assert isinstance(u, UserInput)
        assert u.city == "Banashankari"
        assert u.price_max == 600.0
        assert u.price_min is None

    def test_with_max_price(self):
        u = get_validated_input("Bangalore", max_price=1000)
        assert u.price_max == 1000.0

    def test_with_min_max_range(self):
        u = get_validated_input("Koramangala", min_price=300, max_price=800)
        assert u.price_min == 300.0
        assert u.price_max == 800.0

    def test_city_stripped(self):
        u = get_validated_input("  Banashankari  ", price=500)
        assert u.city == "Banashankari"

    def test_invalid_city_raises(self):
        with pytest.raises(ValueError) as exc:
            get_validated_input("", price=600)
        assert "empty" in str(exc.value).lower() or "City" in str(exc.value)

    def test_invalid_price_raises(self):
        with pytest.raises(ValueError):
            get_validated_input("Bangalore", price=-100)

    def test_missing_price_raises(self):
        with pytest.raises(ValueError) as exc:
            get_validated_input("Bangalore")
        assert "required" in str(exc.value).lower() or "Price" in str(exc.value)

    def test_city_validated_against_list(self):
        allowed = ["Banashankari"]
        get_validated_input("Banashankari", price=600, allowed_cities=allowed)
        with pytest.raises(ValueError) as exc:
            get_validated_input("Mumbai", price=600, allowed_cities=allowed)
        assert "Mumbai" in str(exc.value) or "not found" in str(exc.value).lower()


class TestUserInput:
    """Tests for UserInput dataclass."""

    def test_price_min_greater_than_max_raises(self):
        with pytest.raises(ValueError):
            UserInput(city="X", price_max=300, price_min=500)
