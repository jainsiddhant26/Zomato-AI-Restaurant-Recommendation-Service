"""STEP 3: Integrate data loading, preprocessing, and filtering by user input."""

from typing import Optional

import pandas as pd

from config import COL_APPROX_COST_CLEAN, COL_LISTED_IN_CITY
from src.input_handler import UserInput


def filter_by_city_and_price(
    df: pd.DataFrame,
    city: str,
    price_max: float,
    price_min: Optional[float] = None,
) -> pd.DataFrame:
    """
    Filter preprocessed DataFrame by city and price range.

    - City: case-insensitive exact match on `listed_in(city)`.
    - Price: `approx_cost_clean` <= price_max; if price_min set, >= price_min.
    - Rows with missing approx_cost_clean are excluded from price filter.

    Args:
        df: Preprocessed DataFrame (must have COL_LISTED_IN_CITY, COL_APPROX_COST_CLEAN).
        city: City or area name.
        price_max: Maximum approx cost for two.
        price_min: Optional minimum approx cost for two.

    Returns:
        Filtered DataFrame (copy).
    """
    df = df.copy()
    city_clean = str(city).strip().lower()

    # Normalize listed_in(city) for comparison
    city_col = df[COL_LISTED_IN_CITY].fillna("").astype(str).str.strip().str.lower()
    mask_city = city_col == city_clean

    # Price: require valid numeric cost
    mask_price_max = df[COL_APPROX_COST_CLEAN].notna() & (df[COL_APPROX_COST_CLEAN] <= price_max)
    mask_price = mask_price_max
    if price_min is not None:
        mask_price = mask_price_max & (df[COL_APPROX_COST_CLEAN] >= price_min)

    return df[mask_city & mask_price].reset_index(drop=True)


def run_pipeline(user_input: UserInput, use_cache: bool = True) -> pd.DataFrame:
    """
    Load data, preprocess, and filter by user input (city and price).

    Args:
        user_input: Validated UserInput (city, price_max, price_min).
        use_cache: Passed to load_and_preprocess.

    Returns:
        Filtered DataFrame of candidate restaurants.
    """
    from src.preprocess import load_and_preprocess

    df = load_and_preprocess(use_cache=use_cache)
    return filter_by_city_and_price(
        df,
        city=user_input.city,
        price_max=user_input.price_max,
        price_min=user_input.price_min,
    )


if __name__ == "__main__":
    from src.input_handler import get_validated_input

    user_input = get_validated_input("Banashankari", price=600)
    candidates = run_pipeline(user_input)
    print(f"Candidates: {len(candidates)}")
    print(candidates[["name", "listed_in(city)", "approx_cost_clean", "rate_num"]].head(10).to_string())
