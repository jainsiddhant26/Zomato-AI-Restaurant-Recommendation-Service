"""Tests for cli.py - STEP 2 command-line interface."""

import sys
from io import StringIO
from unittest.mock import patch

import pytest

from src.cli import main, parse_args
from src.input_handler import UserInput


class TestParseArgs:
    """Tests for parse_args."""

    def test_requires_city(self):
        with pytest.raises(SystemExit):
            parse_args(["--price", "600"])

    def test_parses_city_and_price(self):
        args = parse_args(["--city", "Banashankari", "--price", "600"])
        assert args.city == "Banashankari"
        assert args.price == 600.0
        assert args.max_price is None
        assert args.min_price is None

    def test_parses_max_price(self):
        args = parse_args(["--city", "Bangalore", "--max-price", "1000"])
        assert args.city == "Bangalore"
        assert args.max_price == 1000.0

    def test_parses_min_max_range(self):
        args = parse_args([
            "--city", "Koramangala",
            "--min-price", "300",
            "--max-price", "800",
        ])
        assert args.min_price == 300.0
        assert args.max_price == 800.0

    def test_validate_city_flag(self):
        args = parse_args(["--city", "X", "--price", "500", "--validate-city"])
        assert args.validate_city is True


class TestMain:
    """Tests for main() - exit codes and output."""

    def test_main_success_prints_and_returns_user_input(self, capsys):
        out = main(["--city", "Banashankari", "--price", "600"])
        assert isinstance(out, UserInput)
        assert out.city == "Banashankari"
        assert out.price_max == 600.0
        captured = capsys.readouterr()
        assert "City: Banashankari" in captured.out
        assert "Price (max): 600" in captured.out

    def test_main_missing_price_exits_1(self):
        with pytest.raises(SystemExit) as exc:
            main(["--city", "Bangalore"])
        assert exc.value.code == 1

    def test_main_invalid_price_exits_1(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["--city", "Bangalore", "--price", "-100"])
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err

    def test_main_with_min_max(self, capsys):
        out = main(["--city", "X", "--min-price", "300", "--max-price", "800"])
        assert out.price_min == 300.0
        assert out.price_max == 800.0
        captured = capsys.readouterr()
        assert "Price (min): 300" in captured.out
