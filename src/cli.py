"""STEP 2: Command-line interface for city and price input."""

import argparse
import sys
from pathlib import Path

# Project root for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.input_handler import get_validated_input


def parse_args(args=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Zomato AI Restaurant Recommendation — provide city and budget (price for two).",
    )
    parser.add_argument(
        "--city",
        type=str,
        required=True,
        help="City or area name (e.g. Banashankari, Bangalore)",
    )
    parser.add_argument(
        "--price",
        type=float,
        default=None,
        help="Approx cost for two (max budget). Use with --max-price for range.",
    )
    parser.add_argument(
        "--min-price",
        type=float,
        default=None,
        help="Optional minimum budget (approx cost for two).",
    )
    parser.add_argument(
        "--max-price",
        type=float,
        default=None,
        help="Optional maximum budget. Overrides --price if both set.",
    )
    parser.add_argument(
        "--validate-city",
        action="store_true",
        help="Validate city against dataset (loads data). Omit to skip dataset check.",
    )
    return parser.parse_args(args)


def main(args=None):
    """Run CLI: validate inputs and print parsed UserInput or exit with error."""
    parsed = parse_args(args)

    # Optional: validate city against dataset
    allowed_cities = None
    if parsed.validate_city:
        try:
            from src.preprocess import load_and_preprocess
            from config import COL_LISTED_IN_CITY
            df = load_and_preprocess()
            allowed_cities = df[COL_LISTED_IN_CITY].dropna().astype(str).str.strip().unique().tolist()
        except Exception as e:
            print(f"Warning: Could not load dataset for city validation: {e}", file=sys.stderr)
            allowed_cities = None

    price = parsed.max_price if parsed.max_price is not None else parsed.price
    if price is None:
        print("Error: Provide --price or --max-price.", file=sys.stderr)
        sys.exit(1)

    try:
        user_input = get_validated_input(
            city=parsed.city,
            price=parsed.price,
            min_price=parsed.min_price,
            max_price=parsed.max_price,
            allowed_cities=allowed_cities,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"City: {user_input.city}")
    print(f"Price (max): {user_input.price_max}")
    if user_input.price_min is not None:
        print(f"Price (min): {user_input.price_min}")
    return user_input


if __name__ == "__main__":
    main()
