"""Configuration for Zomato AI Restaurant Recommendation Service."""

from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
CACHE_PATH = DATA_DIR / "zomato_data.parquet"

# Dataset
DATASET_NAME = "ManikaSaini/zomato-restaurant-recommendation"
DATASET_SPLIT = "train"

# Column names (as in dataset)
COL_APPROX_COST = "approx_cost(for two people)"
COL_LISTED_IN_CITY = "listed_in(city)"
COL_RATE = "rate"
COL_VOTES = "votes"

# Preprocessed column names
COL_APPROX_COST_CLEAN = "approx_cost_clean"
COL_RATE_NUM = "rate_num"

# Recommendation
TOP_N = 10
