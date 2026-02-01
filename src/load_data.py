"""STEP 1: Load Zomato dataset from Hugging Face with optional caching."""

import sys
from pathlib import Path

import pandas as pd
from datasets import load_dataset

# Add project root to path for config import
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import CACHE_PATH, DATA_DIR, DATASET_NAME, DATASET_SPLIT


def load_zomato_dataset(use_cache: bool = True) -> pd.DataFrame:
    """
    Load the Zomato restaurant dataset.

    Loads from Hugging Face Datasets. If use_cache is True and a cached parquet
    file exists, returns from cache. Otherwise fetches from Hugging Face and
    optionally caches.

    Args:
        use_cache: If True, load from cache when available and save after fetch.

    Returns:
        DataFrame with raw Zomato restaurant data.
    """
    if use_cache and CACHE_PATH.exists():
        return pd.read_parquet(CACHE_PATH)

    dataset = load_dataset(DATASET_NAME, split=DATASET_SPLIT)
    df = dataset.to_pandas()

    if use_cache:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        df.to_parquet(CACHE_PATH, index=False)

    return df


def load_zomato_dataset_fresh() -> pd.DataFrame:
    """
    Load dataset directly from Hugging Face, ignoring cache.

    Returns:
        DataFrame with raw Zomato restaurant data.
    """
    return load_zomato_dataset(use_cache=False)


def clear_cache() -> bool:
    """Remove cached parquet file. Returns True if file was deleted."""
    if CACHE_PATH.exists():
        CACHE_PATH.unlink()
        return True
    return False


if __name__ == "__main__":
    # Quick sanity check
    df = load_zomato_dataset()
    print(f"Loaded {len(df)} rows")
    print(df.head())
