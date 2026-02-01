"""Tests for load_data.py - STEP 1 data loading."""

from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from src.load_data import clear_cache, load_zomato_dataset, load_zomato_dataset_fresh


def _make_mock_dataset():
    """Create a mock dataset matching Hugging Face structure."""
    return pd.DataFrame({
        "name": ["Restaurant A", "Restaurant B"] * 25000,
        "rate": ["4.1/5", "4.0/5"] * 25000,
        "votes": [100, 200] * 25000,
        "approx_cost(for two people)": ["800", "600"] * 25000,
        "listed_in(city)": ["Banashankari", "Bangalore"] * 25000,
    })


class TestLoadZomatoDataset:
    """Tests for load_zomato_dataset (mocked - no network)."""

    def test_load_returns_dataframe(self):
        """load_zomato_dataset returns a pandas DataFrame."""
        mock_df = _make_mock_dataset()
        with patch("src.load_data.load_dataset") as mock_load:
            mock_load.return_value.to_pandas.return_value = mock_df
            df = load_zomato_dataset(use_cache=False)
        assert isinstance(df, pd.DataFrame)

    def test_load_has_expected_columns(self):
        """Loaded DataFrame has key columns for recommendation."""
        mock_df = _make_mock_dataset()
        with patch("src.load_data.load_dataset") as mock_load:
            mock_load.return_value.to_pandas.return_value = mock_df
            df = load_zomato_dataset(use_cache=False)
        expected = [
            "name",
            "rate",
            "votes",
            "approx_cost(for two people)",
            "listed_in(city)",
        ]
        for col in expected:
            assert col in df.columns, f"Missing column: {col}"

    def test_load_has_rows(self):
        """Loaded DataFrame has non-empty rows."""
        mock_df = _make_mock_dataset()
        with patch("src.load_data.load_dataset") as mock_load:
            mock_load.return_value.to_pandas.return_value = mock_df
            df = load_zomato_dataset(use_cache=False)
        assert len(df) > 0
        assert len(df) >= 50000

    def test_load_use_cache_saves_and_loads(self, tmp_path):
        """When use_cache=True, data is saved and can be loaded from cache."""
        mock_df = _make_mock_dataset()
        with patch("src.load_data.CACHE_PATH", tmp_path / "zomato_data.parquet"):
            with patch("src.load_data.DATA_DIR", tmp_path):
                with patch("src.load_data.load_dataset") as mock_load:
                    mock_load.return_value.to_pandas.return_value = mock_df
                    df1 = load_zomato_dataset(use_cache=True)
                assert (tmp_path / "zomato_data.parquet").exists()

                with patch("src.load_data.load_dataset") as mock_load:
                    df2 = load_zomato_dataset(use_cache=True)
                    mock_load.assert_not_called()

                assert len(df1) == len(df2)
                pd.testing.assert_frame_equal(df1, df2)

    def test_load_fresh_ignores_cache(self, tmp_path):
        """load_zomato_dataset_fresh always fetches (does not use cache)."""
        mock_df = _make_mock_dataset()
        with patch("src.load_data.CACHE_PATH", tmp_path / "zomato_data.parquet"):
            tmp_path.mkdir(parents=True, exist_ok=True)
            pd.DataFrame({"x": [1, 2, 3]}).to_parquet(
                tmp_path / "zomato_data.parquet", index=False
            )

            with patch("src.load_data.load_dataset") as mock_load:
                mock_load.return_value.to_pandas.return_value = mock_df
                df = load_zomato_dataset_fresh()

            assert "name" in df.columns
            assert len(df) >= 50000


class TestClearCache:
    """Tests for clear_cache."""

    def test_clear_cache_when_exists(self, tmp_path):
        """clear_cache removes file when it exists."""
        cache_file = tmp_path / "zomato_data.parquet"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.touch()

        with patch("src.load_data.CACHE_PATH", cache_file):
            result = clear_cache()
            assert result is True
            assert not cache_file.exists()

    def test_clear_cache_when_not_exists(self):
        """clear_cache returns False when file does not exist."""
        with patch("src.load_data.CACHE_PATH", Path("/nonexistent/path/data.parquet")):
            result = clear_cache()
            assert result is False
