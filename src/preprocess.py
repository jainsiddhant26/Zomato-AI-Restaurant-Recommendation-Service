"""STEP 1: Preprocess Zomato dataset for recommendation pipeline."""

import re
from typing import Optional

import pandas as pd

from config import (
    COL_APPROX_COST,
    COL_APPROX_COST_CLEAN,
    COL_LISTED_IN_CITY,
    COL_RATE,
    COL_RATE_NUM,
    COL_VOTES,
)


def _parse_rate(value) -> Optional[float]:
    """
    Parse rate string to numeric (e.g., '4.1/5' -> 4.1).

    Handles: '4.1/5', '4.0/5', 'NEW', '-', NaN, etc.
    """
    if pd.isna(value) or value in ("NEW", "-", "", None):
        return None
    value = str(value).strip()
    match = re.search(r"(\d+\.?\d*)\s*/\s*5", value, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except (ValueError, TypeError):
            pass
    return None


def _parse_approx_cost(value) -> Optional[float]:
    """
    Parse approx cost to numeric.

    Handles: '800', '1,000', '500-1000' (uses max), NaN.
    """
    if pd.isna(value) or value in ("", None):
        return None
    value = str(value).strip()
    # Remove commas
    value = value.replace(",", "")
    # Handle range like "500-1000" -> use max (upper bound for filtering)
    if "-" in value:
        parts = value.split("-")
        try:
            nums = [float(p.strip()) for p in parts if p.strip()]
            return max(nums) if nums else None
        except (ValueError, TypeError):
            return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def preprocess_zomato_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess Zomato DataFrame for the recommendation pipeline.

    - Parses `rate` to numeric (rate_num)
    - Parses `approx_cost(for two people)` to numeric (approx_cost_clean)
    - Normalizes `listed_in(city)` for case-insensitive matching
    - Keeps original columns intact; adds new derived columns

    Args:
        df: Raw Zomato DataFrame.

    Returns:
        DataFrame with added columns: rate_num, approx_cost_clean.
        Rows with invalid rate/cost remain; derived cols may be NaN.
    """
    df = df.copy()

    # Parse rate to numeric
    df[COL_RATE_NUM] = df[COL_RATE].apply(_parse_rate)

    # Parse approx cost to numeric
    if COL_APPROX_COST in df.columns:
        df[COL_APPROX_COST_CLEAN] = df[COL_APPROX_COST].apply(_parse_approx_cost)
    else:
        df[COL_APPROX_COST_CLEAN] = None

    # Ensure votes is numeric
    if COL_VOTES in df.columns:
        df[COL_VOTES] = pd.to_numeric(df[COL_VOTES], errors="coerce").fillna(0).astype(int)

    return df


def load_and_preprocess(use_cache: bool = True) -> pd.DataFrame:
    """
    Load Zomato data and preprocess in one call.

    Args:
        use_cache: Passed to load_zomato_dataset.

    Returns:
        Preprocessed DataFrame.
    """
    from src.load_data import load_zomato_dataset

    df = load_zomato_dataset(use_cache=use_cache)
    return preprocess_zomato_data(df)


if __name__ == "__main__":
    from src.load_data import load_zomato_dataset

    df = load_zomato_dataset()
    df = preprocess_zomato_data(df)
    print(df[[COL_RATE, COL_RATE_NUM, COL_APPROX_COST, COL_APPROX_COST_CLEAN]].head(10))
