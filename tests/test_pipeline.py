"""Tests for pipeline.py - STEP 3 integrate (load, preprocess, filter)."""

from unittest.mock import patch

import pandas as pd
import pytest

from config import COL_APPROX_COST_CLEAN, COL_LISTED_IN_CITY
from src.input_handler import UserInput
from src.pipeline import filter_by_city_and_price, run_pipeline


def _make_sample_df():
    """Preprocessed-style DataFrame for unit tests."""
    return pd.DataFrame({
        "name": ["Rest A", "Rest B", "Rest C", "Rest D", "Rest E"],
        COL_LISTED_IN_CITY: ["Banashankari", "Banashankari", "Koramangala", "Banashankari", "Bangalore"],
        COL_APPROX_COST_CLEAN: [500.0, 600.0, 800.0, 400.0, 700.0],
        "rate_num": [4.1, 4.0, 3.8, 4.2, 4.5],
    })


class TestFilterByCityAndPrice:
    """Tests for filter_by_city_and_price."""

    def test_filter_by_city_exact_match(self):
        """Filter by city (case-insensitive)."""
        df = _make_sample_df()
        out = filter_by_city_and_price(df, city="Banashankari", price_max=1000)
        assert len(out) == 3
        assert set(out["name"].tolist()) == {"Rest A", "Rest B", "Rest D"}

    def test_filter_by_city_case_insensitive(self):
        """City match is case-insensitive."""
        df = _make_sample_df()
        out = filter_by_city_and_price(df, city="BANASHANKARI", price_max=1000)
        assert len(out) == 3
        out2 = filter_by_city_and_price(df, city="banashankari", price_max=1000)
        assert len(out2) == 3

    def test_filter_by_price_max(self):
        """Only rows with approx_cost_clean <= price_max."""
        df = _make_sample_df()
        out = filter_by_city_and_price(df, city="Banashankari", price_max=550)
        assert len(out) == 2  # Rest A 500, Rest D 400
        assert out[COL_APPROX_COST_CLEAN].max() <= 550

    def test_filter_by_city_and_price_together(self):
        """City and price filters applied together."""
        df = _make_sample_df()
        out = filter_by_city_and_price(df, city="Banashankari", price_max=500)
        assert len(out) == 2  # Rest A 500, Rest D 400
        out2 = filter_by_city_and_price(df, city="Banashankari", price_max=450)
        assert len(out2) == 1
        assert out2["name"].iloc[0] == "Rest D"

    def test_filter_with_price_min(self):
        """When price_min set, cost must be >= price_min and <= price_max."""
        df = _make_sample_df()
        out = filter_by_city_and_price(
            df, city="Banashankari", price_max=600, price_min=450
        )
        assert len(out) == 2  # Rest A 500, Rest B 600
        assert out[COL_APPROX_COST_CLEAN].min() >= 450
        assert out[COL_APPROX_COST_CLEAN].max() <= 600

    def test_empty_result(self):
        """No matching city or price returns empty DataFrame."""
        df = _make_sample_df()
        out = filter_by_city_and_price(df, city="Mumbai", price_max=1000)
        assert len(out) == 0
        out2 = filter_by_city_and_price(df, city="Banashankari", price_max=100)
        assert len(out2) == 0

    def test_does_not_modify_original(self):
        """Original DataFrame is not modified."""
        df = _make_sample_df()
        original_len = len(df)
        filter_by_city_and_price(df, city="Banashankari", price_max=600)
        assert len(df) == original_len

    def test_handles_missing_cost(self):
        """Rows with NaN approx_cost_clean are excluded from price filter."""
        df = _make_sample_df()
        df.loc[0, COL_APPROX_COST_CLEAN] = pd.NA
        out = filter_by_city_and_price(df, city="Banashankari", price_max=1000)
        # Rest A has NA cost so excluded; Rest B, Rest D remain
        assert len(out) == 2
        assert out[COL_APPROX_COST_CLEAN].notna().all()


class TestRunPipeline:
    """Tests for run_pipeline (with mocked load)."""

    def test_run_pipeline_returns_filtered_df(self):
        """run_pipeline returns DataFrame filtered by UserInput."""
        user_input = UserInput(city="Banashankari", price_max=600)
        sample_df = _make_sample_df()

        with patch("src.preprocess.load_and_preprocess", return_value=sample_df):
            out = run_pipeline(user_input, use_cache=True)

        assert isinstance(out, pd.DataFrame)
        assert len(out) == 3  # Rest A 500, Rest B 600, Rest D 400 in Banashankari <= 600
        assert (out[COL_LISTED_IN_CITY].str.lower() == "banashankari").all()
        assert (out[COL_APPROX_COST_CLEAN] <= 600).all()

    def test_run_pipeline_with_price_min(self):
        """run_pipeline respects price_min from UserInput."""
        user_input = UserInput(city="Banashankari", price_max=600, price_min=450)
        sample_df = _make_sample_df()

        with patch("src.preprocess.load_and_preprocess", return_value=sample_df):
            out = run_pipeline(user_input, use_cache=True)

        assert len(out) == 2  # Rest A 500, Rest B 600
        assert (out[COL_APPROX_COST_CLEAN] >= 450).all()


@pytest.mark.integration
class TestPipelineIntegration:
    """Integration test with real data (requires dataset)."""

    def test_run_pipeline_real_data_returns_candidates(self):
        """With real data, run_pipeline returns non-empty candidates for known city/price."""
        from src.input_handler import get_validated_input

        user_input = get_validated_input("Banashankari", price=800)
        candidates = run_pipeline(user_input, use_cache=True)
        assert isinstance(candidates, pd.DataFrame)
        assert len(candidates) > 0
        assert COL_LISTED_IN_CITY in candidates.columns
        assert COL_APPROX_COST_CLEAN in candidates.columns
        assert (candidates[COL_APPROX_COST_CLEAN] <= 800).all()
