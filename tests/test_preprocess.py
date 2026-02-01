"""Tests for preprocess.py - STEP 1 preprocessing."""

import numpy as np
import pandas as pd
import pytest

from config import COL_APPROX_COST, COL_APPROX_COST_CLEAN, COL_RATE, COL_RATE_NUM, COL_VOTES
from src.preprocess import (
    _parse_approx_cost,
    _parse_rate,
    preprocess_zomato_data,
)


class TestParseRate:
    """Tests for _parse_rate."""

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("4.1/5", 4.1),
            ("4.0/5", 4.0),
            ("5/5", 5.0),
            ("3.5/5", 3.5),
            (" 4.2 / 5 ", 4.2),
        ],
    )
    def test_valid_rate_formats(self, value, expected):
        """Valid rate strings parse correctly."""
        assert _parse_rate(value) == expected

    @pytest.mark.parametrize(
        "value",
        ["NEW", "-", "", None, np.nan],
    )
    def test_invalid_rate_returns_none(self, value):
        """Invalid rate values return None."""
        assert _parse_rate(value) is None


class TestParseApproxCost:
    """Tests for _parse_approx_cost."""

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("800", 800.0),
            ("300", 300.0),
            ("1,000", 1000.0),
            ("2,500", 2500.0),
        ],
    )
    def test_single_values(self, value, expected):
        """Single cost values parse correctly."""
        assert _parse_approx_cost(value) == expected

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("500-1000", 1000.0),
            ("300-600", 600.0),
        ],
    )
    def test_range_uses_max(self, value, expected):
        """Range format uses max value (upper bound)."""
        assert _parse_approx_cost(value) == expected

    @pytest.mark.parametrize(
        "value",
        ["", None, np.nan],
    )
    def test_empty_returns_none(self, value):
        """Empty values return None."""
        assert _parse_approx_cost(value) is None


class TestPreprocessZomatoData:
    """Tests for preprocess_zomato_data."""

    @pytest.fixture
    def sample_df(self):
        """Sample raw DataFrame for preprocessing."""
        return pd.DataFrame({
            "name": ["Restaurant A", "Restaurant B", "Restaurant C"],
            COL_RATE: ["4.1/5", "NEW", "3.8/5"],
            COL_VOTES: ["100", "50", "200"],
            COL_APPROX_COST: ["800", "500-1000", "300"],
        })

    def test_adds_rate_num_column(self, sample_df):
        """Preprocessing adds rate_num column."""
        result = preprocess_zomato_data(sample_df)
        assert COL_RATE_NUM in result.columns
        assert result[COL_RATE_NUM].iloc[0] == 4.1
        assert pd.isna(result[COL_RATE_NUM].iloc[1])
        assert result[COL_RATE_NUM].iloc[2] == 3.8

    def test_adds_approx_cost_clean_column(self, sample_df):
        """Preprocessing adds approx_cost_clean column."""
        result = preprocess_zomato_data(sample_df)
        assert COL_APPROX_COST_CLEAN in result.columns
        assert result[COL_APPROX_COST_CLEAN].iloc[0] == 800.0
        assert result[COL_APPROX_COST_CLEAN].iloc[1] == 1000.0
        assert result[COL_APPROX_COST_CLEAN].iloc[2] == 300.0

    def test_votes_converted_to_int(self, sample_df):
        """Votes column is converted to numeric."""
        result = preprocess_zomato_data(sample_df)
        assert result[COL_VOTES].dtype in (np.int64, np.int32, "int64", "int32")

    def test_does_not_modify_original(self, sample_df):
        """Original DataFrame is not modified in place."""
        original = sample_df.copy()
        preprocess_zomato_data(sample_df)
        pd.testing.assert_frame_equal(sample_df, original)

    def test_handles_missing_approx_cost_column(self):
        """Preprocess handles missing approx_cost column gracefully."""
        df = pd.DataFrame({COL_RATE: ["4.0/5"], COL_VOTES: [100]})
        result = preprocess_zomato_data(df)
        assert COL_APPROX_COST_CLEAN in result.columns
        assert pd.isna(result[COL_APPROX_COST_CLEAN].iloc[0])


@pytest.mark.integration
class TestPreprocessIntegration:
    """Integration tests with real dataset (requires network on first run)."""

    def test_preprocess_real_data(self):
        """Preprocess works on loaded dataset."""
        from src.load_data import load_zomato_dataset

        df = load_zomato_dataset(use_cache=False)
        result = preprocess_zomato_data(df)

        assert len(result) == len(df)
        assert COL_RATE_NUM in result.columns
        assert COL_APPROX_COST_CLEAN in result.columns

        # At least some valid rate parses
        valid_rates = result[COL_RATE_NUM].dropna()
        assert len(valid_rates) > 0
        assert valid_rates.min() >= 0
        assert valid_rates.max() <= 5

        # At least some valid cost parses
        valid_costs = result[COL_APPROX_COST_CLEAN].dropna()
        assert len(valid_costs) > 0
