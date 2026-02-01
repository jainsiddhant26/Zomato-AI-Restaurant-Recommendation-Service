"""STEP 2: Parse and validate user input (city and price)."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class UserInput:
    """Validated user input for restaurant recommendation."""

    city: str
    price_max: float
    price_min: Optional[float] = None

    def __post_init__(self):
        self.city = self.city.strip()
        if self.price_min is not None and self.price_min > self.price_max:
            raise ValueError("price_min must be <= price_max")


def validate_city(
    city: str,
    *,
    allowed_cities: Optional[list[str]] = None,
) -> tuple[bool, str]:
    """
    Validate city input.

    Args:
        city: User-provided city string.
        allowed_cities: If provided, city must be in this list (case-insensitive).

    Returns:
        (is_valid, error_message). error_message is empty when valid.
    """
    if not city or not str(city).strip():
        return False, "City cannot be empty."
    city_clean = str(city).strip()
    if allowed_cities is not None:
        allowed_lower = {c.strip().lower() for c in allowed_cities if c}
        if city_clean.lower() not in allowed_lower:
            return False, f"City '{city_clean}' not found in dataset. Choose from: {', '.join(sorted(allowed_lower)[:10])}{'...' if len(allowed_lower) > 10 else ''}"
    return True, ""


def parse_price(value: str) -> Optional[float]:
    """
    Parse price string to float.

    Accepts integers and decimals. Returns None for invalid input.
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        cleaned = str(value).strip().replace(",", "")
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def validate_price(
    price: Optional[float] = None,
    *,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> tuple[bool, str]:
    """
    Validate price or price range.

    At least one of price (single max) or max_price must be provided.

    Args:
        price: Single price (interpreted as max budget).
        min_price: Optional minimum budget.
        max_price: Optional maximum budget (overrides price if both set).

    Returns:
        (is_valid, error_message).
    """
    max_val = max_price if max_price is not None else price
    if max_val is None:
        return False, "Price (or max-price) is required."
    parsed_max = parse_price(str(max_val)) if not isinstance(max_val, (int, float)) else max_val
    if parsed_max is None:
        return False, "Price must be a valid number."
    if parsed_max <= 0:
        return False, "Price must be positive."

    min_val = min_price
    parsed_min = None
    if min_val is not None:
        parsed_min = parse_price(str(min_val)) if not isinstance(min_val, (int, float)) else min_val
        if parsed_min is None:
            return False, "Min price must be a valid number."
        if parsed_min < 0:
            return False, "Min price cannot be negative."
        if parsed_min > parsed_max:
            return False, "Min price cannot be greater than max price."

    return True, ""


def get_validated_input(
    city: str,
    price: Optional[float] = None,
    *,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    allowed_cities: Optional[list[str]] = None,
) -> UserInput:
    """
    Validate city and price and return a UserInput.

    Args:
        city: City name.
        price: Single max budget (used if max_price not set).
        min_price: Optional min budget.
        max_price: Optional max budget.
        allowed_cities: Optional list of valid city names.

    Returns:
        UserInput with city, price_min, price_max.

    Raises:
        ValueError: If validation fails (with message).
    """
    ok, msg = validate_city(city, allowed_cities=allowed_cities)
    if not ok:
        raise ValueError(msg)

    max_val = max_price if max_price is not None else price
    if max_val is None:
        raise ValueError("Price (or max-price) is required.")
    parsed_max = parse_price(str(max_val)) if not isinstance(max_val, (int, float)) else max_val
    if parsed_max is None or parsed_max <= 0:
        raise ValueError("Price must be a positive number.")

    parsed_min = None
    if min_price is not None:
        parsed_min = parse_price(str(min_price)) if not isinstance(min_price, (int, float)) else min_price
        if parsed_min is None or parsed_min < 0 or parsed_min > parsed_max:
            raise ValueError("Invalid min price or min > max.")

    return UserInput(city=city.strip(), price_max=float(parsed_max), price_min=parsed_min)
